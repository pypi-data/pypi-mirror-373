from math import ceil, floor

from pyPhasesRecordloader import AnnotationInvalid, AnnotationNotFound, Event
from pyPhasesRecordloader.recordLoaders.XMLAnnotationLoader import XMLAnnotationLoader


class AliceRMLLoader(XMLAnnotationLoader):
    smoothLightsAnnotation = 30
    stageMap = {
        "NotScored": "undefined",
        "Wake": "W",
        "NonREM1": "N1",
        "NonREM2": "N2",
        "NonREM3": "N3",
        "REM": "R",
    }

    annotationPaths = {
        "NeuroAdultAASMStaging": [
            "ScoringData",
            "StagingData",
            "UserStaging",
            "NeuroAdultAASMStaging",
        ],
        "BodyPositionState": ["BodyPositionState"],
        "Comments": ["ScoringData", "Events"],
    }

    position = {
        "Up": "Up",
        "Supine": "Supine",
        "Left": "Left",
        "Prone": "Prone",
        "Right": "Right",
    }

    graphoMap = {
        "AlphaActivity-eeg": "AlphaActivity-eeg",
        "RapidEyeMovement-eog": "RapidEyeMovement",
        "SlowEyeMovement-eog": "SlowEyeMovement",
        "Spindle-eeg": "Spindle-eeg",
    }

    eventMapArousal = {
        # "arousal_spontaneous", "arousal_plm", "", "arousal_bruxism", "arousal_noise"
        # "NasalSnore": "arousal_snore",
        "CheyneStokesRespiration": "resp_cheynestokesbreath",
        "RERA": "arousal_rera",
        "Arousal": "arousal",
    }
    eventMapMovements = {
        "LegMovement": "LegMovement",
    }
    eventMapArtefacts = {
        "ChannelFail": "ChannelFail",
    }

    eventMapApnea = {
        "ObstructiveApnea": "resp_obstructiveapnea",
        "CentralApnea": "resp_centralapnea",
        "Hypopnea": "resp_hypopnea",
        "MixedApnea": "resp_mixedapnea",
    }

    eventMapSao2 = {
        "RelativeDesaturation": "spo2_desaturation",
    }

    eventMapCardiac = {
        "HeartRateRise": "hr_rise",
    }

    def __init__(self) -> None:
        super().__init__()

        self.annotations = []
        self.metaXML = None
        self.lightOff = 0
        self.lightOn = None
        self.annotationFrequency = 1
        self.minApneaDuration = 0
        self.xmlNameSpace = "http://www.respironics.com/PatientStudy.xsd"

    def loadClassification(
        self,
        path,
        eventMap,
        eventname=lambda tag: tag.get("Type"),
        durationAttribute=None,
        startAttribute="Start",
        defaultState="ignore",
        minDuration=0,
        replaceName=None,
        filter=lambda _: True,
    ):
        tags = self.getXMLPath(self.metaXML, path)
        if tags is None:
            raise AnnotationNotFound(path)

        notused = []
        for tag in tags:
            name = eventname(tag)
            startValue = tag.get(startAttribute)
            if startValue is None:
                raise AnnotationInvalid(path + [startAttribute])
            start = int(float(startValue) * self.annotationFrequency)
            # if the name is in the eventMap it will be added to the annotations
            if name in eventMap and filter(tag):
                if replaceName:
                    eventName = replaceName(tag)
                else:
                    eventName = eventMap[name]

                if durationAttribute is not None:
                    # if there is a duration the event will be saved as as 2 events:
                    # startTime, "(eventName"
                    # endTime, "eventName)"
                    durationValue = tag.get(durationAttribute)
                    if durationValue is None:
                        raise AnnotationInvalid(path + [durationValue])

                    durationInSeconds = float(durationValue)
                    if durationInSeconds > minDuration:
                        duration = int(durationInSeconds * self.annotationFrequency)
                        self.annotations.append([start, "(" + eventName])
                        self.annotations.append([start + duration - 1, eventName + ")"])
                else:
                    # if its without a duration, it is considered a permanent state change
                    # that will persist until it is changed again
                    self.annotations.append([start, eventName])

            else:
                notused.append(name)

        return set(notused)

    def loadEvents(
        self,
        path,
        eventMap,
        eventname=lambda tag: tag.get("Type"),
        durationAttribute=None,
        startAttribute="Start",
        defaultState="ignore",
        minDuration=0,
        replaceName=None,
        filter=lambda _: True,
        extractAttributes=[],
        extractChilds=[],
    ):
        tags = self.getXMLPath(self.metaXML, path)
        if tags is None:
            raise AnnotationNotFound(path)

        events = []
        lastDefaultEvent = None
        for tag in tags:
            name = eventname(tag)
            startInSeconds = tag.get(startAttribute)

            if startInSeconds is None:
                raise AnnotationInvalid(path + [startAttribute])

            if name in eventMap and filter(tag):
                event = Event()
                event.start = float(startInSeconds)

                event.manual = not tag.get("Machine") == "true"

                data = {}
                for a in extractAttributes:
                    data[a] = tag.get(a)

                for a in extractChilds:
                    data[a] = self.getXMLPath(tag, [a]).text

                event.data = data

                if replaceName:
                    event.name = replaceName(tag)
                else:
                    event.name = eventMap[name]

                if durationAttribute is not None:
                    durationValue = tag.get(durationAttribute)
                    if durationValue is None:
                        raise AnnotationInvalid(path + [durationValue])

                    durationInSeconds = float(durationValue)

                    if durationInSeconds > minDuration:
                        event.duration = durationInSeconds
                        events.append(event)
                else:
                    if lastDefaultEvent is not None:
                        lastDefaultEvent.duration = event.start - lastDefaultEvent.start
                    events.append(event)
                    lastDefaultEvent = event

        if lastDefaultEvent is not None and self.lightOn is not None:
            lastDefaultEvent.duration = self.lightOn - lastDefaultEvent.start

        return events

    def loadAnnotation(self, rmlFile):
        self.loadXmlFile(rmlFile)
        self.annotations = []

        lightOff = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions", "Session", "LightsOff"])
        self.lightOff = 0 if lightOff is None or lightOff.text is None else int(lightOff.text)

        lightOn = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions", "Session", "LightsOn"])
        self.lightOn = None if lightOn is None or lightOn.text is None else int(lightOn.text)

        duration = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions", "Session", "Duration"])
        self.recordDuration = None if duration is None or duration.text is None else int(duration.text)

        # the next step is required to overwrite the edf record duration since the last part is not relevant
        # check for min duration see  acq_522138949 where duration = lightOff
        if self.lightOn is None and self.recordDuration is not None and self.recordDuration > self.lightOff:
            self.lightOn = self.recordDuration

        if self.smoothLightsAnnotation > 0:
            self.lightOff = int(self.smoothLightsAnnotation * ceil(self.lightOff / self.smoothLightsAnnotation))
            if self.lightOn is not None:
                self.lightOn = int(self.smoothLightsAnnotation * floor(self.lightOn / self.smoothLightsAnnotation))

        channelNames = {
            c.get("EdfSignal"): self.getXMLPath(c, ["Label"]).text
            for c in self.getXMLPath(self.metaXML, ["ChannelConfig", "Channels"])
        }

        allEvents = []

        allEvents += self.loadEvents(
            ["ScoringData", "StagingData", "UserStaging", "NeuroAdultAASMStaging"],
            self.stageMap,
        )

        allEvents += self.loadEvents(
            ["BodyPositionState"],
            self.position,
            eventname=lambda tag: tag.get("Position"),
        )

        allEvents += self.loadEvents(
            ["ScoringData", "Events"],
            self.eventMapArousal,
            eventname=lambda tag: self.getXMLPath(tag, ["Comment"]).text if tag.get("Type") == "Comment" else tag.get("Type"),
            durationAttribute="Duration",
        )

        def getLegPosition(tag):
            channelIndex = self.getXMLPath(tag, ["LegMovement"]).get("EdfSignal")
            if channelIndex != "-1":  # channel can be "-1" see acq_552406419
                if channelIndex not in channelNames:
                    self.logError("The Channel for Legmovment does not exist!")
                    return "Left"
                channelName = channelNames[channelIndex]
                if channelName not in ["Bein li", "BeinLi", "BeinRe", "Bein re", "BEIN.re", "BEIN.li", "Bein_re", "Bein_li"]:
                    self.logWarning("Leg ChannelName %s not known" % (channelName))
                return "Left" if channelName in ["Bein li", "BeinLi", "BEIN.li", "Bein_li"] else "Right"
            else:
                return "Left"

        if "forceLegChannel" in self.classificationConfig:
            edfChannel = self.classificationConfig["forceLegChannel"]
            edfChannelId = self.channelMap[edfChannel]
            legMovements = self.loadEvents(
                ["ScoringData", "Events"],
                self.eventMapMovements,
                eventname=lambda tag: tag.get("Type"),
                durationAttribute="Duration",
                filter=lambda tag: self.getXMLPath(tag, ["LegMovement"]).get("EdfSignal") == str(edfChannelId),
            )
        else:
            legMovements = self.loadEvents(
                ["ScoringData", "Events"],
                self.eventMapMovements,
                eventname=lambda tag: tag.get("Type"),
                replaceName=lambda tag: "LegMovement-%s" % (getLegPosition(tag)),
                durationAttribute="Duration",
            )

        # allEvents.append(legMovements)
        allEvents += legMovements

        allEvents += self.loadEvents(
            ["ScoringData", "Events"],
            self.eventMapApnea,
            eventname=lambda tag: tag.get("Type"),
            durationAttribute="Duration",
            minDuration=self.minApneaDuration,
            extractAttributes=["Machine"],
        )

        allEvents += self.loadEvents(
            ["ScoringData", "Events"],
            self.eventMapArtefacts,
            eventname=lambda tag: tag.get("Type"),
            replaceName=lambda tag: "fail-channel%s" % (self.getXMLPath(tag, ["ChannelFail"]).get("EdfSignal")),
            durationAttribute="Duration",
        )

        allEvents += self.loadEvents(
            ["ScoringData", "Events"],
            self.eventMapSao2,
            eventname=lambda tag: tag.get("Type"),
            durationAttribute="Duration",
            extractChilds=["O2Before", "O2Min"],
        )

        allEvents += self.loadEvents(
            ["ScoringData", "Events"],
            self.eventMapCardiac,
            eventname=lambda tag: tag.get("Type"),
            durationAttribute="Duration",
        )

        # TODO: check for multi segments/sessions
        sessions = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions"])
        segments = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions", "Session", "Segment"])
        if sessions is not None and len(sessions) > 1:
            self.logError("unexpected")

        if segments is not None and len(segments) > 1:
            self.logError("unexpected")

        return allEvents

    def getMetaData(self, rmlFile):
        self.loadXmlFile(rmlFile)
        metadata = {}
        comment = self.getXMLPath(self.metaXML, ["ChannelConfig", "ConfigName"])
        metadata["comment"] = None if comment is None else comment.text

        lightOff = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions", "Session", "LightsOff"])
        metadata["lightOff"] = 0 if lightOff is None or lightOff.text is None else int(lightOff.text)

        lightOn = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions", "Session", "LightsOn"])
        metadata["lightOn"] = None if lightOn is None or lightOn.text is None else int(lightOn.text)
        
        return metadata

