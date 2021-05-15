import requests
import datetime
from appJar import gui
import math
from typing import *
import numpy as np


class GUI:
    def __init__(self):

        self.olaps = 1
        self.blaps = 1
        self.api = API()
        self.ogates = 0
        self.bgates = 0

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
        app.addEntry("IP Addr", 0, colspan=2)
        app.setEntryWidth("IP Addr", 60)
        app.setEntry("IP Addr", "IP: " + self.IP, callFunction=False)
        app.setEntryChangeFunction("IP Addr", self.writeIP)
        app.setEntryAlign("IP Addr", "center")
        app.addButton("help", self.helpFunc, colspan=2)
        app.setButton("help", "Click me for help!")
        app.addLabel("status", "Waiting to connect", colspan=2)
        app.addHorizontalSeparator(colspan=2)
        app.addLabel("clock", "00:00:00", colspan=2)
        app.addHorizontalSeparator(colspan=2)
        app.addLabel("start", "Lap times", colspan=2).config(font="Arial 20 underline bold")
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
        for i in range(1, 6):
            app.addLabel("B" + str(i), "BLap"+str(i), row=i+7, column=0, colspan=1)
            app.setLabelTooltip("B" + str(i), "Gates: ")
            app.setLabelWidth("B"+str(i), 20)
        for i in range(1, 6):
            app.addLabel("O" + str(i), "OLap" + str(i), row=i + 7, column=1, colspan=1)
            app.setLabelTooltip("O" + str(i), "Gates: ")

        app.go()

    def mainclock(self):
        teamLapped = self.api.checkGates()
        if teamLapped:
            if "B" in teamLapped:
                self.app.setLabel("B"+str(self.blaps), "BLap"+str(self.blaps)+str(self.clock-self.start))
                self.blaps += 1
            if "O" in teamLapped:
                self.app.setLabel("O"+str(self.blaps), "OLap"+str(self.blaps)+str(self.clock-self.start))
                self.blaps += 1
            if "b" in teamLapped:
                self.bgates += 1
                self.bgates %= 6
                gates: str = self.app.getLabelTooltip("B"+str(self.blaps))
                gates: str = gates[7:]
                gates: List = gates.split(" ")
                lastGate = gates[-1].split(": ")
                if not lastGate[-1]:
                    lastGate[-1] = [self.start]
                gates.append("Gate "+str(self.bgates+1)+": "+str(self.clock-lastGate))
            if "o" in teamLapped:
                self.ogates += 1
                self.ogates %= 6
                gates: str = self.app.getLabelTooltip("O" + str(self.olaps))
                gates: str = gates[7:]
                gates: List = gates.split(" ")
                lastGate = gates[-1].split(": ")
                if not lastGate[-1]:
                    lastGate[-1] = [self.start]
                gates.append("Gate " + str(self.ogates+1) + ": " + str(self.clock - lastGate))

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
            self.api = API()
            self.timer = self.app.after(1, self.clockRun)
            return
        if start[1] == "r":
            self.app.setLabel("status", "ready")


class API:
    def __init__(self):
        config = open("config.txt", "r")
        self.IP = config.read().splitlines()[0]
        config.close()
        self.orangeGates = [((15, 11), (2, -2), 4),
                            ((15, 11), (2, -2), -4),
                            ((1, -1), (1, -1), -35),
                            ((-11, -15), (2, -2), -4),
                            ((-11, -15), (2, -2), 4),
                            ((1, -1), (1, -1), 35)]
        self.blueGates = [#((-11, -15), (2, -2), (5, 3)),
            ((-11, -15), (2, -2), -4),
                          ((-11, -15), (2, -2), 4),
                          ((1, -1), (1, -1), 35),
                          ((15, 11), (2, -2), 4),
                          ((15, 11), (2, -2), -4),
                          ((1, -1), (1, -1), -35)]
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

    def checkRay(self, lastPos, currentPos, gate):
        """
        Bunch of complicated ass maths I don't entirely understand ngl
        :param lastPos:
        :param currentPos:
        :param gate:
        :return: bool
        """
        planeNormal = np.array([0, 1, 0])
        planePoint = np.array([gate[0][0], gate[1, 0], gate[2]])  # Any point on the plane

        # Define ray
        rayDirection = np.array([currentPos[0]-lastPos[0], currentPos[1]-lastPos[1], currentPos[2]-lastPos[2]])
        rayPoint = np.array(currentPos)  # Any point along the ray

        Psi = self.LinePlaneCollision(planeNormal, planePoint, rayDirection, rayPoint)
        print("intersection at", Psi)

    def LinePlaneCollision(self, planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):
        """
        yes I stole this code. It comes from
        https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane#Python
        as of 15/05/2021
        :param planeNormal:
        :param planePoint:
        :param rayDirection:
        :param rayPoint:
        :param epsilon:
        :return:
        """
        ndotu = planeNormal.dot(rayDirection)
        if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or line is within plane")

        w = rayPoint - planePoint
        si = -planeNormal.dot(w) / ndotu
        Psi = w + si * rayDirection + planePoint
        return Psi

    def checkGates(self, res=None):
        #print(self.counterBlue)
        if not res:
            res = self.get()
        if not res:
            return
        returnStr = ""
        blueGate = self.blueGates[self.counterBlue]
        orangeGate = self.orangeGates[self.counterOrange]
        #print(res["teams"][0])
        bluePlayers = res["teams"][0]["players"]
        orangePlayers = res["teams"][3]["players"]
        bluePosAverage = self.averagePosition(bluePlayers[0]["head"]["position"], bluePlayers[1]["head"]["position"])
        orangePosAverage = self.averagePosition(orangePlayers[0]["head"]["position"], orangePlayers[1]["head"]["position"])
        if self.checkRay(self.bluePositions[-1], bluePosAverage, self.blueGates[self.counterBlue]):
            returnStr += "b"
            self.counterBlue = (self.counterBlue + 1) % len(self.blueGates)
            #say("blue passed through gate"+str(self.counterBlue))
            if self.counterBlue == 0:
                self.orangeLaps += 1
                returnStr += "B"
        if self.checkRay(self.orangePositions[-1], orangePosAverage, self.orangeGates[self.counterOrange]):
            self.counterOrange = (self.counterOrange + 1) % len(self.orangeGates)
            returnStr += "o"
            #say("orange passed through gate"+str(self.counterOrange))
            if self.counterOrange == 0:
                self.orangeLaps += 1
                returnStr += "O"
        self.orangePositions.append(orangePosAverage)
        self.bluePositions.append(bluePosAverage)
        #print(bluePosAverage)
        return returnStr

    def checkStart(self, res=None):
        if not res:
            res = self.get()
        if not res:
            return False, "e"
        try:
            #print(res)
            teams = res["teams"]
            #print(teams)
            blue = teams[0]["players"]
            orange = teams[1]
            start = False
            if len(teams) > 3:
                orange = teams[3]
            orange = orange["players"]
            if len(blue) < 2 or len(orange) < 2:
                return False, "p"
            if res["game_clock"] < 0.1:
                start = True
            if res["game_status"] != "playing":
                return start, "r"

            return False, "e"
        except KeyError:
            return False, "l"

appGui = GUI()
