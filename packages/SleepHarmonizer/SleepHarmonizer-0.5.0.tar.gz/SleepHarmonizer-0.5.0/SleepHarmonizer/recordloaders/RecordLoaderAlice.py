from pathlib import Path

from SleepHarmonizer.PSGEventManager import PSGEventManager
from pyPhasesRecordloader.recordLoaders.EDFRecordLoader import EDFRecordLoader
from pyPhasesRecordloader import Event


from .AliceRMLLoader import AliceRMLLoader
from .AliceTextReportLoader import AliceTextReportLoader


class RecordLoaderAlice(EDFRecordLoader):
    def __init__(self, filePath, targetSignals, targetSignalTypes, optionalSignals=None, combineChannels=None) -> None:

        super().__init__(
            filePath=filePath,
            targetSignals=targetSignals,
            targetSignalTypes=targetSignalTypes,
            optionalSignals=optionalSignals,
            combineChannels=combineChannels,
        )
        self.validateOnly = False
        self.exportsEventArray = True

    def getFilePathSignal(self, recordId):
        return f"{self.filePath}/{recordId}/{recordId}.edf"

    def getFilePathAnnotation(self, recordId):
        return f"{self.filePath}/{recordId}/{recordId}.rml"

    def getFilePathTxt(self, recordId):
        return f"{self.filePath}/{recordId}/{recordId}.txt"

    def existAnnotation(self, recordId):
        return Path(self.getFilePathAnnotation(recordId)).exists()

    def exist(self, recordId):
        return self.existAnnotation() and Path(self.getFilePathSignal(recordId)).exists()

    def getEventList(self, recordName, targetFrequency=1):
        metaXML = self.getFilePathAnnotation(recordName)
        rmlLoader = self.getAliceLoader()
        eventArray = rmlLoader.loadAnnotation(metaXML)
        self.lightOff = rmlLoader.lightOff
        self.lightOn = rmlLoader.lightOn

        if self.lightOn is not None:
            eventArray.append(Event(name="lightOn", start=self.lightOn, frequency=0))

        if self.lightOff is not None:
            eventArray.append(Event(name="lightOff", start=self.lightOff, frequency=0))

        if targetFrequency != 1:
            [event.updateFrequency(targetFrequency) for event in eventArray]

        return self.fixEvents(eventArray)

    def getAliceLoader(self):

        rmlLoader = AliceRMLLoader()
        rmlLoader.classificationConfig = self.classificationConfig
        rmlLoader.channelMap = self.channelMap

        return rmlLoader

    # def fillRecordFromTxtReport(self, recordName, record):
    #     reportFile = self.getFilePath(recordName) + ".txt"
    #     loader = AliceTextReportLoader()
    #     loader.addTxtReport(reportFile, record)

    def getMetaData(self, recordName):

        metaData = super().getMetaData(recordName)
        metaData.update(self.getAliceLoader().getMetaData(self.getFilePathAnnotation(recordName)))
        metaData.update(AliceTextReportLoader().getMetaData(self.getFilePathTxt(recordName)))

        return metaData

    def fixArousal(self, df):
        em = PSGEventManager()

        em.dfAppendGroups(
            df,
            "arousal",
            "sleepStage",
            newGroupName="sleepStage-15",
            offsetStart=-15.1,
            fixedDuration=15.1,
        )

        removeQuery = "(name == 'arousal' and `sleepStage-15` == 'W')"
        rem = df.query(removeQuery)
        df.drop(rem.index, inplace=True)

        # if labelName == "SleepArousalsExtended":
        #     em.dfAppendGroups(
        #         df,
        #         "arousal",
        #         "limb",
        #         newGroupName="limb-arousal",
        #         offsetStart=-0.6,
        #         offsetEnd=0.6,
        #     )
        #     em.dfAppendGroups(
        #         df,
        #         "arousal",
        #         "sleepStage",
        #         newGroupName="woke-arousal",
        #         offsetStart=-0.5,
        #         offsetEnd=15.1,
        #     )
        #     df.loc[df.query("name == 'arousal' and `limb-arousal` != ''").index, "name"] = "arousal_limb"
        #     df.loc[df.query("name == 'arousal'").index, "name"] = "arousal_none"
        #     df.loc[df.query("name == 'arousal_rera'").index, "name"] = "arousal_rera_man"
        return df

    def fixSPO2Events(self, df):
        em = PSGEventManager()
        em.dfAppendGroups(
            df,
            "spo2",
            "sleepStage",
            newGroupName="sleepStage-15",
            offsetStart=-15.1,
            fixedDuration=15.2,
        )

        df["o2diff"] = df.apply(
            lambda row: (
                (float(row["data"]["O2Before"]) - float(row["data"]["O2Min"]))
                if "O2Min" in row["data"] and "O2Before" in row["data"]
                else None
            ),
            axis=1,
        )
        removeQuery = "(group == 'spo2' and manual == False and (o2diff < 3 or (`sleepStage-15` == 'W')))"
        rem = df.query(removeQuery, engine="python")

        df.drop(rem.index, inplace=True)
        return df
    
    def fixApnea(self, df):
        em = PSGEventManager()

        em.dfAppendGroups(
            df,
            "apnea",
            "sleepStage",
            newGroupName="sleepStageStart15",
            offsetStart=-15.1,
            fixedDuration=15.1,
        )

        arousalOffset = 5
        em.dfAppendGroups(
            df,
            "apnea",
            "arousal",
            newGroupName="arousal",
            offsetStart=0,
            offsetEnd=arousalOffset,
        )

        desatOffset = 10
        em.dfAppendGroups(
            df,
            "apnea",
            "spo2",
            newGroupName="desaturation",
            offsetStart=0,
            offsetEnd=desatOffset,
        )

        removeQuery = "(group == 'apnea' and manual == False  and (duration < 10 or sleepStageStart15 == 'W' or (name == 'resp_hypopnea' and arousal != 'arousal' and desaturation == '')))"
        rem = df.query(removeQuery)
        df.drop(rem.index, inplace=True)
        return df
    
    def fixLM(self, df):
        em = PSGEventManager()
        em.dfAppendGroups(
            df,
            "limb",
            "sleepStage",
            newGroupName="sleepStage-15",
            offsetStart=-15.1,
            fixedDuration=15.2,
        )
        em.dfAppendGroups(
            df,
            "limb",
            "apnea",
            newGroupName="apnea",
            offsetStart=-0.5,
            offsetEnd=0.5,
        )
        em.dfAppendGroups(
            df,
            "limb",
            "arousal",
            newGroupName="arousal",
            offsetStart=-0.5,
            offsetEnd=0.5,
        )

        removeQuery = (
            "(group == 'limb' and (`sleepStage-15` == 'W' or apnea != '' or arousal.str.contains('arousal_rera')))"
        )
        rem = df.query(removeQuery, engine="python")
        df.drop(rem.index, inplace=True)
        return df

    def fixEvents(self, eventArray):
        em = PSGEventManager()
        df = em.getDataframeFromEvents(eventArray)
        # legmovement depend on apnea + arousal
        # apnea depends on spo2events + arousal
        df = self.fixArousal(df)
        df = self.fixSPO2Events(df)
        df = self.fixApnea(df)
        df = self.fixLM(df)
        return [Event.fromdict(r) for r in df.T.to_dict().values()]
