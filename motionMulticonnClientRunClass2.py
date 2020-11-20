import multiconnClientClass2
import selectors
import sys
import time

#use this command to run program:
#python C:/Users/chris/Documents/programming/github/uv/wifiCommunications/motionMulticonnClientRunClass2.py



if __name__ == '__main__':
    startTime = time.time()

    if len(sys.argv) == 1:#read the arguments inputted by the person running the code; if nothing is inputted use default initializations for the variables
        startName = "defaultLightName"
        startState = "ON"
    if len(sys.argv) > 1:
        startName = sys.argv[1]
    if len(sys.argv) > 2:
        startState = sys.argv[2]

    sel = selectors.DefaultSelector()


    #variables that simulate the actual state of the light
    currentActualState = startState
    currentActualName = startName
    currentActualTime = 0

    #initialStateList is in the format [initial actualState, actualName, actualCurrentTime]
    initialStateList = [currentActualState, currentActualName, 0]

    wifiComm = multiconnClientClass2.wifiCommunicator(sel, initialStateList)

    context = "IDLE"

    #timerTestAlreadyDone = False
    motionTime = 10
    motionEndTime = 30

    while True:
        wifiComm.checkWifi()#check wifi signals
        #now can check wifiComm.lightModuleDict to see what the wifi is instructing the light to do
        #print(wifiComm.getState())
        wifiState = wifiComm.getState() #format [connectionStatus ("CONNECTED"/"NOTYETCONNECTED"/"DISCONNECTED"), wifiState ("ON"/"OFF"), wifiName (string), resetTime (bool)]
        #if the wif-commanded state or name has changed, then simulate changing the actual name and state of the light
        '''
        if wifiState[2] is not None:
            currentActualName = wifiState[2]
        if wifiState[1] is not None:
            currentActualState = wifiState[1]

        if wifiState[3] == True:
            print("TIMER RESET REQUESTED")
        '''
        if wifiState[0] == "CONNECTED":
            currentActualName = wifiState[2]
        if wifiState[0] == "CONNECTED":
            currentActualState = wifiState[1]

        if wifiState[0] == "DISCONNECTED":
            currentActualState = "OFF" #turn light off if it has disconnected from the base station...

        #Check for timer reset request
        if wifiState[0] == "CONNECTED" and wifiState[3] == True:
            print("TIMER RESET REQUESTED")
        

        currentTime = time.time()


        '''
        if currentTime - startTime > motionTime  and timerTestAlreadyDone == False:
            currentActualState = "OFF"
            context = "MOTION"
            timerTestAlreadyDone = True
            wifiComm.confirmState(currentActualState, currentActualName, None, context)# parameter format: "ON"/"OFF", nameOfLight (string), currentTime, context ("IDLE"/"MOTION"/"TIMER"/"ON")
        elif currentActualState == "ON" and (currentTime-startTime < motionTime or currentTime - startTime > motionEndTime):
            context = "ON"
            wifiComm.confirmState(currentActualState, currentActualName, None, context)# parameter format: "ON"/"OFF", nameOfLight (string), currentTime, context ("IDLE"/"MOTION"/"TIMER"/"ON")
        elif currentActualState == "OFF" and (currentTime-startTime < motionTime or currentTime - startTime > motionEndTime):
            context = "IDLE"
            wifiComm.confirmState(currentActualState, currentActualName, None, context)# parameter format: "ON"/"OFF", nameOfLight (string), currentTime, context ("IDLE"/"MOTION"/"TIMER"/"ON")
        #print(wifiState)
        '''
        if currentTime - startTime > motionTime and currentTime - startTime < motionEndTime:
            currentActualState = "OFF"
            context = "MOTION"
            wifiComm.confirmState(currentActualState, currentActualName, None, context)# parameter format: "ON"/"OFF", nameOfLight (string), currentTime, context ("IDLE"/"MOTION"/"TIMER"/"ON")
        elif currentActualState == "ON":
            context = "ON"
            wifiComm.confirmState(currentActualState, currentActualName, None, context)# parameter format: "ON"/"OFF", nameOfLight (string), currentTime, context ("IDLE"/"MOTION"/"TIMER"/"ON")
        elif currentActualState == "OFF":
            context = "IDLE"
            wifiComm.confirmState(currentActualState, currentActualName, None, context)# parameter format: "ON"/"OFF", nameOfLight (string), currentTime, context ("IDLE"/"MOTION"/"TIMER"/"ON")
        #print(wifiState)
            
    sel.close()