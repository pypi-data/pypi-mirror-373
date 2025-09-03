import shutil
from pathlib import Path

from pyPhases import Phase
from pyPhases.util import BatchProgress
from pyPhasesRecordloader import AnnotationNotFound, ChannelsNotPresent, Event, RecordLoader

from SleepHarmonizer.PSGEventManager import PSGEventManager
from SleepHarmonizer.recordwriter.RecordWriter import RecordWriter
from SleepHarmonizer.SignalPreprocessing import SignalPreprocessing


class Export(Phase):
    skipExisting = True
    useMultiThreading = True
    useDigitalSignals = True
    prepareEventsFor = None

    def getAnnotationsFromDf(self, df):
        return df.T.to_dict().values()

    def getLightEvents(self, lightOff, lightOn):
        lightEvents = []
        if lightOn is not None:
            lightEvents.append(Event.fromdict({"start": lightOn, "duration": 0, "name": "lightOn"}))
        if lightOff > 0:
            lightEvents.append(Event.fromdict({"start": lightOff, "duration": 0, "name": "lightOff"}))

        return lightEvents
    
    def preprocessing(self, recordSignal, preprocessingConfig):
        targetFrequency = preprocessingConfig["targetFrequency"]
        recordSignal.targetFrequency = targetFrequency

        signalPreprocessing = SignalPreprocessing.getInstance(preprocessingConfig)

        # set the target frequency for the signal to get the correct signal length
        signalPreprocessing.preprocessingSignal(recordSignal)

    def exportRecord(self, recordName):
        rw = self.recordWriter
        rl = self.recordLoader

        if self.skipExisting and rw.exist(recordName):
            self.log(f"Record {recordName} skipped because it already exists")
            return

        try:
            psgSignal, events = rl.loadRecord(recordName)
            metaData = rl.getMetaData(recordName)
            metaData["sessionId"] = rl.getSessionId(recordName)
            metaData["subjectId"] = rl.getSubjectId(recordName)
            metaData["patientCode"] = metaData["subjectId"] if "patientCod" not in metaData or metaData["patientCode"] == "" else metaData["patientCode"]
            metaData["dicom"] = rl.getDICOMMetadata(recordName)
            
            em = PSGEventManager()

            events += self.getLightEvents(rl.lightOff, rl.lightOn)
            events = em.getDataframeFromEvents(events)

            # tailor psg signal
            keepSignals = self.getConfig("export.channels", None)
            psgSignal.reduceSignals(keepSignals)

            allowEventsConfig = self.getConfig("export.annotations", None)
            allowEvents = []
            if allowEventsConfig is not None:
                for ev in allowEventsConfig:
                    if ev in em.eventGroups and ev:
                        allowEvents += em.eventGroups[ev]
                    else:
                        allowEvents.append(ev)

                events = events.query("name in @allowEvents")

            annotations = self.getAnnotationsFromDf(events)

            # signal preprocessing / harmonizing
            targetFrequency = self.preProcessingConfig["targetFrequency"]
            signalProcessor = SignalPreprocessing.getInstance(self.preProcessingConfig)
            psgSignal.targetFrequency = targetFrequency
            signalProcessor.preprocessingSignal(psgSignal)
            rw.metaData = metaData
            # write the harmonized signal into an edf
            rw.createFolderStructure()
            tmpRecordName = recordName + "-tmp"

            rw.writeSignals(tmpRecordName, psgSignal.signals, annotations, signalIsDigital=self.useDigitalSignals)
            shutil.move(rw.getFilePath(tmpRecordName), rw.getFilePath(recordName))

        except AnnotationNotFound as e:
            self.logError(f"not all required annotation exist for {recordName}")
        except ChannelsNotPresent as e:
            self.logError(f"not all required channels exist for {recordName}: {e.channels}")

    def main(self):
        self.events = None
        self.annotations = []

        self.exportPath = self.getConfig("export-path")
        if not Path(self.exportPath).exists():
            Path(self.exportPath).mkdir(parents=True, exist_ok=True)

        recordId = self.getConfig("recordId", False)
        if not recordId:
            recordIds = self.project.getData("allDBRecordIds", list)
            # flatten grouped record ids
            recordIds = [recordId for groupedRecords in recordIds.values() for recordId in groupedRecords]
        else:
            self.useMultiThreading = False
            recordIds = [recordId]

        bp = BatchProgress()
        bp.asynchronous = True
        bp.useMultiThreading = self.useMultiThreading

        self.recordLoader = RecordLoader.get()
        self.recordWriter = RecordWriter.get()
        self.recordLoader.useDigitalSignals = self.useDigitalSignals

        self.preProcessingConfig = self.getConfig("preprocessing")
        bp.start(self.exportRecord, batchList=recordIds)
