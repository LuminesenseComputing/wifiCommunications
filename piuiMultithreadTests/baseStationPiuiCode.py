
import functools
import os
import random
import time
from piui import PiUi
import threading
import sys
import socket
import selectors
import types
import time
import queue

current_dir = os.path.dirname(os.path.abspath(__file__))



#####THE MOSTLY ORIGINAL DEMO PIUI PROGRAM
########################################

#stores info about a light module for display on the screen
class lightModulePiUiInfo:
    def __init__(self, port):
        self.port = port
        self.displayTime = 0
        self.state = "UNKNOWN" #can be ON, OFF, TURNING_ON, TURNING_OFF, UNKNOWN if using the toggle system; can be ON, OFF, CHANGING_STATE, UNKNOWN if using the button light control system
        self.name = "UNKNOWN" #an example of a light name

class DemoPiUi(object):

    def __init__(self, queuey, receiveQueuey):
        self.title = None
        self.txt = None
        self.img = None
        self.ui = PiUi(img_dir=os.path.join(current_dir, 'imgs'))
        self.src = "sunset.png"
        self.queuey = queuey #ADDED FOR WIFI - queue to hold the outgoing messages, connecting the piui and wifi program threads
        self.receiveQueuey = receiveQueuey
        self.piuiLightDict = {}#this dict will store the active lights' lightModulePiUiInfo; keys are the port numbers
        self.currentPage = None
        self.titles = {} #this is a dictionary that is used by the toggle page to remember the title for each light; keys are the port numbers
        self.nameInputs = {} #this is a dictionary that is used by the toggle page to remember the name textbox for each light; keys are port numbers


    def page_static(self):
        self.page = self.ui.new_ui_page(title="Static Content", prev_text="Back",
            onprevclick=self.main_menu)
        self.page.add_textbox("Add a mobile UI to your Raspberry Pi project", "h1")
        self.page.add_element("hr")
        self.page.add_textbox("You can use any static HTML element " + 
            "in your UI and <b>regular</b> <i>HTML</i> <u>formatting</u>.", "p")
        self.page.add_element("hr")
        self.page.add_textbox("Your python code can update page contents at any time.", "p")
        update = self.page.add_textbox("Like this...", "h2")
        time.sleep(2)
        for a in range(1, 5):
            update.set_text(str(a))
            time.sleep(1)

    def page_buttons(self):
        self.page = self.ui.new_ui_page(title="Buttons", prev_text="Back", onprevclick=self.main_menu)
        self.title = self.page.add_textbox("Buttons!", "h1")
        plus = self.page.add_button("Up Button &uarr;", self.onupclick)
        minus = self.page.add_button("Down Button &darr;", self.ondownclick)

    def page_input(self):
        self.page = self.ui.new_ui_page(title="Input", prev_text="Back", onprevclick=self.main_menu)
        self.title = self.page.add_textbox("Input", "h1")
        self.txt = self.page.add_input("text", "Name")
        button = self.page.add_button("Say Hello", self.onhelloclick)

    def page_images(self):
        self.page = self.ui.new_ui_page(title="Images", prev_text="Back", onprevclick=self.main_menu)
        self.img = self.page.add_image("sunset.png")
        self.page.add_element('br')
        button = self.page.add_button("Change The Picture", self.onpicclick)


    def page_lightController(self):
        self.currentPage = "page_lightController"#still need to test to make sure this actually sets the variable correctly when loading a page

        self.page = self.ui.new_ui_page(title="Light Control", prev_text="Back", onprevclick=self.main_menu)
        self.list = self.page.add_list()
        self.titles = {} # A dictionary that stores the textboxes on the page
        self.nameInputs = {}
        for port in self.piuiLightDict:
            self.titles[port] = self.page.add_textbox("Light name: "+ self.piuiLightDict[port].name+"\nPort: " +str(port)+" Status: " + self.piuiLightDict[port].state, "h2")
            self.nameInputs[port] = self.page.add_input("text", "Change Nickname")
            self.page.add_button("Save Nickname", functools.partial(self.onLightNameType, port))  
            self.page.add_button("Change State", functools.partial(self.onLightControlClick, port))

        while True:
            incomingSignal = self.lightReceiveEvent()
            if incomingSignal is not None:#if there is a message coming from the wifi, process it
                self.processSignal(incomingSignal)

    def processSignal(self, incomingSignal):
        signal = incomingSignal.split(":")[1]
        port = int(incomingSignal.split(":")[0])
        if signal == "CONNECTED":
            self.piuiLightDict[port] = lightModulePiUiInfo(port)#add a new light module to the piui light dictionary
            self.lightCommandEvent(str(port)+":"+"GETSTATE_COMMAND")#get the current state of the light the just connected
            self.lightCommandEvent(str(port)+":"+"GETNAME")#get the current state of the light the just connected
            if self.currentPage == "page_lightController":
                self.titles[port] = self.page.add_textbox("Light name: "+ self.piuiLightDict[port].name+"\nPort: " +str(port)+" Status: " + self.piuiLightDict[port].state, "h2")
                self.nameInputs[port] = self.page.add_input("text", "Change Nickname")
                self.page.add_button("Save Nickname", functools.partial(self.onLightNameType, port)) 
                self.page.add_button("Change State", functools.partial(self.onLightControlClick, port))
        elif signal == "ON" or signal=="CON_ON":
            self.piuiLightDict[port].state = "ON"
            if self.currentPage == "page_lightController":
                self.changeLightText(port)
        elif signal =="OFF" or signal == "CON_OFF":
            self.piuiLightDict[port].state = "OFF"
            if self.currentPage == "page_lightController":
                self.changeLightText(port)
        elif signal=="CLOSED":
            self.piuiLightDict.pop(port,None)#if the light has become offline, take it out of the dictionary
            if self.currentPage == "page_lightController":
                self.page_lightController()#reset the page_toggles page if a light has been taken out of the list
        elif signal == "STATEIS_ON":#this is a reply to the request to get the current state of the light
            self.piuiLightDict[port].state = "ON"
            if self.currentPage == "page_lightController":
                self.changeLightText(port)
        elif signal == "STATEIS_OFF":#this is a reply to the request to get the current state of the light
            self.piuiLightDict[port].state = "OFF"
            if self.currentPage == "page_lightController":
                self.changeLightText(port)
        elif isinstance(signal,str) and len(signal) > 6 and signal[0:7] == "NAMEIS_":#this is a reply to the request to get the current name of the light
            self.piuiLightDict[port].name = signal[7:]
            if self.currentPage == "page_lightController":
                self.changeLightText(port)
        elif isinstance(signal,str) and len(signal) > 11 and signal[0:12] == "NAMECHANGED_":
            self.piuiLightDict[port].name = signal[12:]
            if self.currentPage == "page_lightController":
                self.changeLightText(port)

    '''
    def page_console(self):
        con = self.ui.console(title="Console", prev_text="Back", onprevclick=self.main_menu)
        con.print_line("Hello Console!")
    '''
    def main_menu(self):
        self.currentPage = "main_menu"#SHOULD TEST IF THIS ACTUYALLY CHANGES WHEN GOING BACK TO MAIN<<<<<<<<<<<<<<<<<<<<
        self.page = self.ui.new_ui_page(title="PiUi")
        self.list = self.page.add_list()
        self.list.add_item("Static Content", chevron=True, onclick=self.page_static)
        self.list.add_item("Buttons", chevron=True, onclick=self.page_buttons)
        self.list.add_item("Input", chevron=True, onclick=self.page_input)
        self.list.add_item("Images", chevron=True, onclick=self.page_images)
        self.list.add_item("Light Control", chevron=True, onclick=self.page_lightController)
        #self.list.add_item("Console!", chevron=True, onclick=self.page_console)
        while True:
            incomingSignal = self.lightReceiveEvent()
            if incomingSignal is not None:
                self.processSignal(incomingSignal)


        self.ui.done()

    def main(self):
        self.main_menu()
        self.ui.done()
        print("THREE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def onupclick(self):
        self.title.set_text("Up ")
        #self.queuey.put("yo")#THIS LINE IS AN EXAMPLE OF SENDING A MESSAGE TO THE WIFI THREAD OF THE PROGRAM###########
        print ("Up")

    def ondownclick(self):
        self.title.set_text("Down")
        print ("Down")

    def onhelloclick(self):
        print ("onstartclick")
        self.title.set_text("Hello " + self.txt.get_text())
        print ("Start")

    def onpicclick(self):
        if self.src == "sunset.png":
          self.img.set_src("sunset2.png")
          self.src = "sunset2.png"
        else:
          self.img.set_src("sunset.png")
          self.src = "sunset.png"

    def onLightControlClick(self, port):
        value = "CHANGESTATE_COMMAND"
        self.piuiLightDict[port].state = "CHANGING_STATE"
        self.lightCommandEvent(str(port)+":"+value)
        self.changeLightText(port)

    def onLightNameType(self, port):
        newName = self.nameInputs[port].get_text()
        value = "CHANGENAME_" + newName
        self.piuiLightDict[port].name = "name_changing"
        self.lightCommandEvent(str(port)+":"+value)
        self.changeLightText(port)

    def changeLightText(self, port):
        #index = self.indices[str(port)]
        self.titles[port].set_text("Light name: "+ self.piuiLightDict[port].name+"\nPort: " +str(port)+" Status: " + self.piuiLightDict[port].state)

#AN EXAMPLE OF A POTENTIAL FUNCTION THAT COULD BE USED FOR
#SENDING WIFI MESSAGES FROM PIUI################
    def lightCommandEvent(self, command):
        self.queuey.put(command)

    def lightReceiveEvent(self):
        if not self.receiveQueuey.empty():
            return self.receiveQueuey.get()
        else:
            return None
