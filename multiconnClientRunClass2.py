import multiconnClientClass2
import selectors
import sys


if __name__ == '__main__':
    if len(sys.argv) == 1:#read the arguments inputted by the person running the code; if nothing is inputted use default initializations for the variables
        startName = "defaultLightName"
        startState = "OFF"
    if len(sys.argv) > 1:
        startName = sys.argv[1]
    if len(sys.argv) > 2:
        startState = sys.argv[2]

    sel = selectors.DefaultSelector()

    #initialStateList is in the format [initial actualState, actualName, actualCurrentTime]
    initialStateList = [startState, startName, 0]

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