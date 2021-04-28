import requests
import datetime
from appJar import gui
import math
from typing import *


class GUI:
    def __init__(self):
        self.api = API()

        config = open("config.txt", "r")
        self.IP = config.read().splitlines()[0]
        config.close()

        self.start = datetime.datetime.now()
        self.clock = datetime.datetime.now()

        self.app = gui("VRPL Regrab race timekeeper", stretch="both")
        app = self.app
        app.setSticky("news")
        app.setExpand("vertical")
        # app.setPadding([2, 2])
        app.addEntry("IP Addr", 0)
        app.setEntryWidth("IP Addr", 60)
        app.setEntry("IP Addr", "IP: " + self.IP, callFunction=False)
        app.setEntryChangeFunction("IP Addr", self.writeIP)
        app.setEntryAlign("IP Addr", "center")
        app.addButton("help", self.helpFunc)
        app.setButton("help", "Click me for help!")
        app.addLabel("status", "Waiting to connect")
        app.addHorizontalSeparator()
        app.addLabel("clock", "00:00:00")
        app.addHorizontalSeparator()
        app.addLabel("start", "Lap times").config(font="Arial 20 underline bold")
        self.timer = app.after(1000, self.checkStart)
        app.bindKey("s", self.stopClock)
        app.bindKey("r", self.resetClock)

        app.startSubWindow("help")
        app.label("title", "How do I use this?")
        app.label("ip1",
                  "Enter the IP at the top. By default this is the feedback IP, which is what you use if Echo is running on your pc.")
        app.label("ip2",
                  "If you are on a Quest, connect your Quest to sidequest and enter the IP in the top left. It should be something like 192.168.x.xx.")
        app.label("stop", "To stop the clock, press 's'")
        app.label("reset", "To reset the clock, press 'r'")
        app.stopSubWindow()

        app.after(100, self.mainclock)
        for i in range(10):
            app.addLabel("test" + str(i), "test")
            app.setLabelTooltip("test" + str(i), "gate 1: 00:00:00, gate 1: 00:00:00, gate 1: 00:00:00")
        app.go()

    def mainclock(self):
        self.api.checkGates()
        self.checkStart()
        self.app.after(10, self.mainclock)

    def writeIP(self):
        config = open("config.txt", "r")
        configVals = config.read().splitlines(keepends=True)
        #print(configVals)
        configVals = configVals[1:]
        #print(configVals)
        config.close()
        config = open("config.txt", "w")
        config.write(self.app.getEntry("IP Addr")[4:]+"\n"+"".join(configVals))
        config.close()

    def helpFunc(self):
        self.app.showSubWindow("help")

    def clockSet(self):
        diff = self.clock-self.start
        diff = str(diff)
        diff = diff.replace(".", ":")
        diff = diff.split(":")
        diff = diff[1:]
        # print(diff)
        if len(diff) > 2:
            diff[2] = diff[2][:2]
        self.app.setLabel("clock", ":".join(diff))

    def clockRun(self):
        self.clock = datetime.datetime.now()
        self.clockSet()
        self.timer = self.app.after(1, self.clockRun)

    def stopClock(self):
        self.app.afterCancel(self.timer)

    def resetClock(self):
        self.start = datetime.datetime.now()
        self.clock = datetime.datetime.now()
        # print(self.clock-self.start)
        self.stopClock()

    def checkStart(self):
        #print(".")
        start = self.api.checkStart()
        if type(start) == Dict:
            self.start = datetime.datetime.now()
            self.clock = datetime.datetime.now()
            self.timer = self.app.after(1, self.clockRun)
            return
        if start[1] == "r":
            self.app.setLabel("status", "ready")


class API:
    def __init__(self):
        config = open("config.txt", "r")
        self.IP = config.read().splitlines()[0]
        config.close()
        self.orangeGates = [((15, 11), (2, -2), (4.1, 4)),
                            ((15, 11), (2, -2), (-4, -4.1)),
                            ((1, -1), (1, -1), (-35, -35.1)),
                            ((-11, -15), (2, -2), (-4, -4.1)),
                            ((-11, -15), (2, -2), (4.1, 4)),
                            ((1, -1), (1, -1), (35.1, 35))]
        self.blueGates = [((-11, -15), (2, -2), (-4, -4.1)),
                          ((-11, -15), (2, -2), (4.1, 4)),
                          ((1, -1), (1, -1), (35.1, 35)),
                          ((15, 11), (2, -2), (4.1, 4)),
                          ((15, 11), (2, -2), (-4, -4.1)),
                          ((1, -1), (1, -1), (-35, -35.1))]
        self.counterOrange = 0
        self.counterBlue = 0
        self.orangeLaps = 0
        self.blueLaps = 0
        self.orangePositions = []
        self.bluePositions = []

    def get(self) -> Union[Dict, bool]:
        try:
            res = requests.get("http://"+self.IP+":6721/session", timeout=0.1)
            res = res.json()
            #print(res)
            return res
        except :
            #print("connection error, are you in a game?")
            return False

    def size(self, vector):
        a = vector[0]
        b = vector[1]
        c = vector[2]
        return math.pow((a**2+b**2+c**2), 1/3)

    def averagePosition(self, a, b):
        return (a[0]+b[0])//2, (a[1]+b[1])//2, (a[2]+b[2])//2

    def checkGates(self, res=None):
        print(self.counterBlue)
        if not res:
            res = self.get()
        if not res:
            return
        blueGate = self.blueGates[self.counterBlue]
        orangeGate = self.orangeGates[self.counterOrange]
        #print(res["teams"][0])
        bluePlayers = res["teams"][0]["players"]
        orangePlayers = res["teams"][3]["players"]
        bluePosAverage = self.averagePosition(bluePlayers[0]["head"]["position"], bluePlayers[1]["head"]["position"])
        orangePosAverage = self.averagePosition(orangePlayers[0]["position"], orangePlayers[1]["position"])
        if blueGate[0][0] >= bluePosAverage[0] >= blueGate[0][1] and\
           blueGate[1][0] >= bluePosAverage[1] >= blueGate[1][1] and\
           blueGate[2][0] >= bluePosAverage[2] >= blueGate[2][1]:
            self.counterBlue = (self.counterBlue + 1) % len(self.blueGates)
            #say("passed through gate"+str(self.counterBlue))
            if self.counterBlue == 0:
                self.orangeLaps += 1
        if orangeGate[0][0] > orangePosAverage[0] > orangeGate[0][1] and \
           orangeGate[1][0] > orangePosAverage[1] > orangeGate[1][1] and \
           orangeGate[2][0] > orangePosAverage[2] > orangeGate[2][1]:
            self.counterOrange = (self.counterOrange + 1) % len(self.orangeGates)
            if self.counterOrange == 0:
                self.orangeLaps += 1
        self.orangePositions.append(orangePosAverage)
        self.bluePositions.append(bluePosAverage)
        #print(bluePosAverage)

    def checkStart(self, res=None):
        if not res:
            res = self.get()
        if not res:
            return False, "e"
        try:
            #print(res)
            teams = res["teams"]
            #print(teams)
            blue = teams[1]["players"]
            orange = []
            if len(teams) > 3:
                orange = teams[3]["players"]
            if len(blue) < 2 or len(orange) < 2:
                return False, "p"
            if res["game_status"] != "playing":
                return False, "r"
            if res["game_clock"] < 0.1:
                return True
            return False, "e"
        except KeyError:
            return False, "l"


appGui = GUI()
