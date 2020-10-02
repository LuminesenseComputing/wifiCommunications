import multiconnClientClass2
import selectors

sel = selectors.DefaultSelector()

#initialStateList is in the format [[initial actualState, actualName, actualCurrentTime], ... repeated for each light on this light module]
initialStateList = ["OFF", "lightName", 0]

wifiComm = multiconnClientClass2.wifiCommunicator(sel, initialStateList)

wifiState = None

while True:
    wifiComm.checkWifi()#check wifi signals
    #now can check wifiComm.lightModuleDict to see what the wifi is instructing the light to do
    #print(wifiComm.getState())
    wifiState = wifiComm.getState() #format [connectionStatus ("CONNECTED"/"NOTYETCONNECTED"/"DISCONNECTED"), wifiState ("ON"/"OFF"), wifiName (string), resetTime (bool)]
    #print(wifiState)
    wifiComm.confirmState(wifiState[1], wifiState[2], None, None)# parameter format: "ON"/"OFF", nameOfLight (string), currentTime, context ("IDLE"/"MOTION"/"TIMER"/"ON")
sel.close()