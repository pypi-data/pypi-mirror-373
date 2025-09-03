from pathlib import Path
from SleepHarmonizer.recordloaders.DominoErgLoader import DominoErgLoader

from pyPhasesRecordloader.recordLoaders.EDFRecordLoader import EDFRecordLoader
from pyPhasesRecordloader import AnnotationNotFound
from .DominoAnnotationLoader import DominoAnnotationLoader


class RecordLoaderDomino(EDFRecordLoader):
    possibleNamesSleepstages = ["SchlafProfil", "Schlafprofil"]
    possibleRespEvents = ["Flow Events"]
    possibleArousalEvents = ["Klassifizierte Arousal"]

    def getFileBasePath(self, recrdId):
        return self.filePath + "/" + recrdId

    def getFilePathSignal(self, recordId):
        return self.getFileBasePath(recordId) + "/" + recordId + ".edf"

    def getFilePathAnnotation(self, recordId):
        annotationFolder = self.downloaderConfig.get("annotationFolder", "annotations")
        return self.getFileBasePath(recordId) + f"/{annotationFolder}"
    
    def getErgPath(self, recordId):
        return self.getFileBasePath(recordId) + "/" + recordId + ".erg"

    def existAnnotation(self, recordId):
        return [Path(self.getFilePathAnnotation(recordId) + f"/{n}.txt").exists() for n in self.possibleNamesSleepstages]

    def loadAnnotation(self, recordId, fileNames, valueMap=None, possibleValues=None):
        found = False
        for fileName in fileNames:
            filePath = self.getFilePathAnnotation(recordId)  + "/" + fileName + ".txt"
            if Path(filePath).exists():
               found = True
               break
        
        if not found:
            raise AnnotationNotFound(fileName)
            
        annotationLoader = DominoAnnotationLoader.load(filePath, valueMap, self.annotationFrequency, possibleValues)

        return annotationLoader.events


    def getMetaData(self, recordName):

        metaData = super().getMetaData(recordName)
        # metaData.update(self.getAliceLoader().getMetaData(self.getFilePathAnnotation(recordName)))
        metaData.update(DominoErgLoader().getMetaDataFromFile(self.getErgPath(recordName), DominoErgLoader.relevantRows))
        
        # lightOff = self.getXMLPath(self.metaXML, ["Acquisition", "Sessions", "Session", "LightsOff"])
        # off, on = self.getLightAnnotations()
        # metaData["lightOff"] = off
        # metaData["lightOn"] = on

        return metaData
    
    def getLightAnnotations(self):
        """get light off, on in seconds"""
        lightOff = self.getLastAnnotationTimeByName("Licht aus")
        lightOn = self.getFirstAnnotationTimeByName("Ende der Messung")
        
        if lightOff is None:
            self.logError("Die Annotation 'Licht Aus' wurde nicht gefunden")
        else:
            lightOff = int(lightOff)
        if lightOn is None:
            self.logWarning("Die Annotation 'Ende der Messung' wurde nicht gefunden")
        else:
            lightOn = int(lightOn)

        return lightOff, lightOn
            

    def getEventList(self, recordName, targetFrequency=1):
        self.annotationFrequency = targetFrequency

        eventArray = self.loadAnnotation(
            recordName,
            self.possibleNamesSleepstages,
            {
                "N3": "N3",
                "N2": "N2",
                "N1": "N1",
                "Rem": "R",
                "Wach": "W",
                "Artefakt": "undefined",
            },
        )

        # eventArray = self.loadAnnotation(
        #     recordName,
        #     "Autonome Arousal",
        #     {
        #         "Autonome Arousal": "arousal",
        #     },
        # )
        try:
            eventArray += self.loadAnnotation(
                recordName,
                self.possibleRespEvents,
                {
                    "Obstruktive Apnoe": "resp_obstructiveapnea",
                    "Gemischte Apnoe": "resp_mixedapnea",
                    "Zentrale Apnoe": "resp_centralapnea",
                    "Hypopnoe": "resp_hypopnea",
                    "RERA": "arousal_rera",
                },
                possibleValues=["Obstruktive Apnoe", "Gemischte Apnoe", "Zentrale Apnoe", "Hypopnoe", "RERA"],
            )
        except AnnotationNotFound:
            pass

        try:
            eventArray += self.loadAnnotation(
                recordName,
                self.possibleArousalEvents,
                {

                    "Arousal": "arousal",
                    "Respiratorische Arousal": "arousal_rera",
                    "PLM Arousal": "arousal_plm",
                    "LM Arousal": "arousal_limb",
                    "Schnarchen Arousal": "arousal_snore",
                    "SpO2 Arousal": "arousal",

                    "Arousal (EEG)": "arousal",
                    "Respiratorische Arousal (EEG)": "arousal_rera",
                    "PLM Arousal (EEG)": "arousal_plm",
                    "LM Arousal (EEG)": "arousal_limb",
                    "Schnarchen Arousal (EEG)": "arousal_snore",                
                    "SpO2 Arousal (EEG)": "arousal",

                    "Arousal (Autonome)": "arousal",
                    "Respiratorische Arousal (Autonome)": "arousal_rera",
                    "PLM Arousal (Autonome)": "arousal_plm",
                    "LM Arousal (Autonome)": "arousal_limb",
                    "Schnarchen Arousal (Autonome)": "arousal_snore",                
                    "SpO2 Arousal (Autonome)": "arousal",
                },
                possibleValues=[
                    "Arousal", "Respiratorische Arousal", "PLM Arousal", "LM Arousal", "Schnarchen Arousal", "SpO2 Arousal",
                    "Arousal (EEG)", "Respiratorische Arousal (EEG)", "PLM Arousal (EEG)", "LM Arousal (EEG)", "Schnarchen Arousal (EEG)", "SpO2 Arousal (EEG)",
                    "Arousal (Autonome)", "Respiratorische Arousal (Autonome)", "PLM Arousal (Autonome)", "LM Arousal (Autonome)", "Schnarchen Arousal (Autonome)", "SpO2 Arousal (Autonome)",
                ],
            )
        except AnnotationNotFound:
            pass

        self.lightOff, self.lightOn = self.getLightAnnotations()

        return eventArray
