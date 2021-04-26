import requests
import json
import datetime
from appJar import gui
import math


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
        app.addHorizontalSeparator()
        app.addLabel("clock", "00:00:00")
        app.addHorizontalSeparator()
        app.addLabel("start", "Lap times").config(font="Arial 20 underline bold")
        self.timer = app.after(10, self.checkStart)
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

        for i in range(10):
            app.addLabel("test" + str(i), "test")
            app.setLabelTooltip("test" + str(i), "gate 1: 00:00:00, gate 1: 00:00:00, gate 1: 00:00:00")
        app.go()

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
        print(".")
        if self.api.checkStart():
            self.start = datetime.datetime.now()
            self.clock = datetime.datetime.now()
            self.timer = self.app.after(1, self.clockRun)
        else:
            self.timer = self.app.after(1, self.checkStart)


class API:
    def __init__(self):
        config = open("config.txt", "r")
        self.IP = config.read().splitlines()[0]
        config.close()

    def get(self):
        try:
            res = requests.get("http://"+self.IP+":6721/session")
            res = res.json()
            print(res)
            return res
        except requests.exceptions.ConnectionError:
            print("connection error, are you in a game?")

    def size(self, vector):
        a = vector[0]
        b = vector[1]
        c = vector[2]
        return math.pow((a**2+b**2+c**2), 1/3)

    def checkStart(self, res=None):
        if not res:
            res = self.get()
        if not res:
            return False
        print(res)
        teams = res["teams"]
        print(teams)
        players = teams[1]["players"]
        if len(players) > 3:
            players.append(teams[3]["players"])
        for player in players:
            if self.size(player["velocity"]) > 5:
                return True
        return False


appGui = GUI()
