from datetime import datetime, timedelta

from pyPhases.util.Logger import classLogger
from pyPhasesRecordloader import Event


@classLogger
class DominoAnnotationLoader:
    headers = {
        "Signal ID": "id",
        "Start Time": "startTime",
        "Signal Type": "signalType",
        "Events list": "possibleValues",
        "Rate": "Rate",
        "Unit": "unit",
    }

    def __init__(self):
        self.state = "meta"

        self.id = ""
        self.startTime = None
        self.unit = None
        self.signalType = None
        self.valueMap = {
            'N4': 'N3'
        }
        self.possibleValues = None

        self.targetFrequency = 1
        self.events = []
        self.curOffset = 0
        self.curValue = None
        self.eventStart = 0
        self.distinct = True
        self.lastDistinct = None

    def wrapTime(self, timeInSeconds):
        return int(timeInSeconds) * self.targetFrequency
    
    def addEvent(self, start, end, value):
        duration = end - start
        value = self.valueMap[value] if self.valueMap is not None and value in self.valueMap else value
        self.events.append(Event(name=value, start=start, duration=duration))

    def finishEvent(self):
        if self.curValue is not None and self.curValue != "A":
            start = self.wrapTime(self.eventStart)
            value = self.curValue
            if self.distinct:
                if self.lastDistinct is not None:
                    self.lastDistinct.duration = start - self.lastDistinct.start
                self.addEvent(start, start, value)
                self.lastDistinct = self.events[-1]
            else:
                end = self.wrapTime(self.curOffset)
                self.addEvent(start, end, value)

    def addContentLine(self, line):
        values = [v.strip() for v in line.split(";")]

        if self.signalType == "Discret":
            time, value = values
            # time = "%i.%i.%i "%(self.startTime.)
            # time = datetime.strptime(value, "%d.%m.%Y %H:%M:%S")
            if self.curValue is None or self.curValue != value:
                self.finishEvent()
                self.eventStart = self.curOffset

            self.curValue = value
            self.curOffset += 30
        elif self.signalType == "Impuls":
            time, duration, value = values
            time = datetime.strptime(time.split("-")[0], "%H:%M:%S,%f")
            time = datetime.combine(self.startTime, time.time())
            startOffset = time - self.startTime
            # add a day if its beyond 24h
            if startOffset < timedelta(0):
                startOffset = startOffset + timedelta(days=1)
            
            startOffset = startOffset.total_seconds()
            startOffset = self.wrapTime(startOffset)
            duration = float(duration)

            self.addEvent(startOffset, startOffset+duration, value)

    def validateMeta(self):
        assert self.id is not None
        assert self.startTime is not None
        assert self.possibleValues is not None
        assert self.signalType is not None
        assert self.signalType in ["Discret", "Impuls"], "at the moment only Discret/Impulse signalTypes are supported"

        if self.id == "SchlafProfil\profil":
            assert self.Rate == "30 s", f"at the moment only 30 sec Schlafprofil is supported, failed value {self.Rate}"
            assert self.possibleValues in [["N3", "N2", "N1", "Rem", "Wach", "Artefakt"], ['N4', 'N3', 'N2', 'N1', 'Rem', 'Wach', 'Bewegung']], f"only AASM Schlafprofil is supported, failed value: {self.possibleValues}"

    def parseMetaLine(self, line):
        type, value = [v.strip() for v in line.split(":", 1)]
        type = self.headers[type]

        if type == "startTime":
            try:
                value = datetime.strptime(value, "%d.%m.%Y %H:%M:%S")  # 19.11.2020 19:30:30
            except ValueError:
                try:
                    value = datetime.strptime(value, "%d.%m.%Y")  # 19.11.2020
                except ValueError:
                    value = None

        elif type == "possibleValues":
            value = [v.strip() for v in value.split(",")]

        self.__setattr__(type, value)

    def parseLine(self, line):
        if line == "":
            self.state = "content"
            self.validateMeta()
        elif self.state == "meta":
            self.parseMetaLine(line)
        else:
            self.addContentLine(line)

    def parseLines(self, lines):
        for line in lines:
            self.parseLine(line.strip())
        self.finishEvent()

    @staticmethod
    def load(path, valueMap=None, targetFrequency=1, possibleValues=None):
        dl = DominoAnnotationLoader()
        dl.valueMap = valueMap
        dl.targetFrequency = targetFrequency
        dl.possibleValues = possibleValues

        with open(path, "r", encoding="iso-8859-1") as f:
            content = f.readlines()

        dl.parseLines(content)

        return dl
