# Basic Python Plugin Example
#
# Author: Benjamin CROSASSO
#
"""
<plugin key="LinkyStdMode" name="TeleInfo Linky Standard Mode" author="Benjamin CROSASSO" version="1.0.0" wikilink="https://github.com/bnj-04/LinkyStdMode" externallink="https://www.google.com/">
    <description>
        <h2>Linky Standard Mode Plugin</h2><br/>
        <h3>Configuration</h3>
        Enter the serial port to use /dev/ttyUSB0 for example and enable or not debug mode
    </description>
    <params>
        <param field="SerialPort" label="Serial Port"/>
         <param field="Mode3" label="Debug" width="75px">
            <options>
                <option label="Non" value="0"  default="true" />
                <option label="Oui" value="1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import serial
from datetime import datetime
from datetime import timedelta

class BasePlugin:
    s = None
    enabled = None
    isConnected = False
    isStarted = False
    iDebugLevel = 0
    iDebug = False
    iIndexUnit = 1
    sDeviceName = "LinkyStdMode"
    sDescription = "Linky en mode Standard"
    iType = 250
    iSubType = 1
    iSwitchType = 0


    def __init__(self):
        isConnected = False
        return

    def myDebug(self, message):
        if self.iDebug:
            Domoticz.Log("LinkyStdMode DEBUG " + message)

    def createDevice(self):
        # Only if not already done
        if not self.iIndexUnit in Devices:
            Domoticz.Device(Name=self.sDeviceName,  Unit=self.iIndexUnit, Type=self.iType, Subtype=self.iSubType, Switchtype=self.iSwitchType, Description=self.sDescription, Used=1).Create()
            if not (self.iIndexUnit in Devices):
                Domoticz.Error("Ne peut ajouter le dispositif Linky à la base de données. Vérifiez dans les paramètres de Domoticz que l'ajout de nouveaux dispositifs est autorisé")
                return False
        return True

    def updateDevice(self, cpt, inst):
        # -1.0 for counter because Linky doesn't provide absolute counter value via Enedis website
        sValue = self.getData()
        if sValue is not None:
            self.myDebug("Mets dans la BDD la valeur " + sValue)
            Devices[self.iIndexUnit].Update(nValue=0, sValue=sValue, Type=self.iType, Subtype=self.iSubType, Switchtype=self.iSwitchType)
            return True
        else:
            return False


    def checkCRC(self,t):
        s1 = 0
        d = t[1:-1]
        crc = t[-1:]
        for c in d:
            s1 = (s1 + ord(c))%0x100
        s1 = (s1 & 0x3F) + 0x20
        if s1 == ord(crc):
            return True
        else:
            return False




    def getData(self):

        EAST = "0"
        SINSTS = "0"

        EAIT = "0"
        SINSTI = "0"

        now = datetime.now()

        while EAST == "0" or SINSTS == "0":
            if ((datetime.now() - now) > timedelta(seconds=5)):
                Domoticz.Error("serial timeout")
                break
            a = self.s.read()
            if a != b'\x0A':
                continue
            else:
                t = str(a,'utf-8')
                a = self.s.read()
                while a != b'\x0D':
                    if ((datetime.now() - now) > timedelta(seconds=5)):
                        Domoticz.Error("serial timeout")
                        break
                    t = t + str(a,'utf-8')
                    a = self.s.read()

            if t.find("EAST") > -1:
                if self.checkCRC(t):
                    EAST = t.split('\t')[1]
                    self.myDebug("EAST "+EAST)
                else:
                    Domoticz.Error("CRC ERROR EAST")
                    break

            if t.find("SINSTS") > -1:
                if self.checkCRC(t):
                    SINSTS = t.split('\t')[1]
                    self.myDebug("SINSTS " + SINSTS)
                else:
                    Domoticz.Error("CRC ERROR SINSTS")
                    break


        if EAST=="0" or SINSTS=="0":
            self.myDebug("return none")
            return None
        else:
            return EAST+";0;0;0;"+SINSTS+";0"


    def onStart(self):
        try:
            self.iDebugLevel = int(Parameters["Mode3"])
        except ValueError:
            self.iDebugLevel = 0

        if self.iDebugLevel > 0:
            self.iDebug = True

        self.myDebug("LinkyStdMode - onStart called")
        self.myDebug("LinkyStdMode "+Parameters["SerialPort"])
        self.createDevice()

        try:
            self.s = serial.Serial(Parameters["SerialPort"],9600,bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE,timeout=1,exclusive=True)
            self.isConnected = True
        except SerialException:
            self.isConnected = False
            Domoticz.Error("Erreur lors de l'accès au port série")

        self.isStarted = True





    def onStop(self):
        Domoticz.Log("onStop called")
        self.isStarted = False

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
        self.s.close()

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        self.updateDevice(1,2)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
