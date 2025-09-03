import io
from dataclasses import dataclass
from datetime import timedelta

from pyPhases.util.Logger import classLogger

from teleschlafmedizin.model.recordManager.RecordMeta import RecordAnnotation

from ..RecordManager import RecordWriter
from .TSMRecordManager import Annotation, TSMRecordManager


@dataclass
class DominoAnnotation(Annotation):
    valueMapIndex = {}

    def __init__(self, id="", unit="", rate=None, signalType="Discret", fileName="", **kwargs):
        self.id = id
        self.unit = unit
        self.rate = rate
        self.signalType = signalType
        self.fileName = fileName
        super().__init__(**kwargs)

    @staticmethod
    def createAnnotation(name):
        a = Annotation.createAnnotation(name, DominoAnnotation())

        if name == "NeuroAdultAASMStaging":
            # a.possibleValues = ["N3", "N2", "N1", "Rem", "Wach"]
            a.fileName = "Schlafprofil"
            a.id = "SchlafProfil\profil"
            a.signalType = "Discret"
            a.rate = "30 s"
            a.valueMap = {
                "N3": "N3",
                "N2": "N2",
                "N1": "N1",
                "Rem": "R",
                "Wach": "W",
                "Artefakt": "undefined",
            }
            a.valueMapIndex = {
                "N3": 0,
                "N2": 1,
                "N1": 2,
                "R": 3,
                "W": 4,
                "undefined": 5,
            }
        elif name == "RespiratoryEvents":
            # a.possibleValues = ["N3", "N2", "N1", "Rem", "Wach"]
            a.fileName = "Flow Analyse"
            a.id = "FlowD\flow"
            a.signalType = "Impuls"
            a.unit = "s"
            a.valueMap = {
                "Obstruktive Apnoe": "resp_obstructiveapnea",
                "Hypopnoe": "resp_hypopnea",
                "Zentrale Apnoe": "resp_centralapnea",
                "Gemischte Apnoe": "resp_mixedapnea",
                "Obstruktive Hypopnoe": "resp_hypopnea_obstructive",
                "RERA": "arousal_rera",
                "": "none",
            }
            a.valueMapIndex = {
                "resp_hypopnea": 1,
                "resp_obstructiveapnea": 2,
                "resp_centralapnea": 3,
                "resp_mixedapnea": 4,
                "resp_hypopnea_obstructive": 7,
                "resp_hypopnea_central": 8,
                "arousal_rera": 9,
                "undefined": 5,
            }
            # Apnoe = 0
            # Flußlimitationen = 5
            # Körperlage Event = 6
        else:
            raise Exception("Domino export for %s not supported at the moment" % (name))

        #     signalType="Impuls",
        #     id="KorrelationMA\MAK",
        #     fileName="Klassifikation Arousal",
        #     possibleValues={
        #         "Undefined",
        #         "Respiratorisches Arousal",
        #         "PLM Arousal",
        #         "SpO2 Arousal",
        #         "Kardio Arousal",
        #         "Schnarch Arousal",
        #         "Arousal (EEG)",
        #         "Respiratorisches Arousal (EEG)",
        #         "PLM Arousal (EEG)",
        #         "SpO2 Arousal (EEG)",
        #         "Kardio Arousal (EEG)",
        #         "Schnarch Arousal (EEG)",
        #         "Arousal (EMG)",
        #         "Respiratorisches Arousal (EMG)",
        #         "PLM Arousal (EMG)",
        #         "SpO2 Arousal (EMG)",
        #         "Kardio Arousal (EMG)",
        #         "Schnarch Arousal (EMG)",
        #         "Flusslimitation Arousal",
        #         "Flusslimitation Arousal (EEG)",
        #         "Flusslimitation Arousal (EMG)",
        #         "RERA Arousal",
        #         "LM Arousal",
        #         "LM Arousal (EEG)",
        #         "LM Arousal (EMG)",
        #         "Arousal (Autonom)",
        #         "Respiratorisches Arousal (Autonom)",
        #         "PLM Arousal (Autonom",
        #         "SpO2 Arousal (Autonom)",
        #         "Kardio Arousal (Autonom)",
        #         "Schnarch Arousal (Autonom)",
        #         "Flusslimitation Arousal (Autonom)",
        #         "LM Arousal (Autonom)",
        #         "RERA Arousal (EEG)",
        #         "RERA Arousal (EMG)",
        #         "RERA Arousal (Autonom)",
        #     },

        # Spindel Analyse - Spindel\spindel
        #   Spindel = 0
        #   K-Komplex = 1

        # EOG Analyse - EOG\REM
        #   EM = 0
        #   link = 1

        # Schnarch-Analyse - Snore\snore
        #   Schnarchen = 0

        # SpO2 Analyse - Spo2\SpO2_Analyse
        #   Entsättigung = 0
        #   Körperlage Event = 1

        # LM Analyse - PLM\plm
        #   I-Marker = 0
        #   P-Marker = 1
        #   LM Resp = 2
        #   LM Körperlage = 3

        # Hertzfrequenzanalyse DOMINO - Kardio\Kardio_Analyse
        #   Akzeleration = 1
        #   Dezeleration = 2
        #   Arrhythmie = 3
        #   Tachykardie (breiter QRS Komplex) = 8
        #   Tachykardie (schmaler QRS Komplex) = 9
        #   Asystole = 10

        # Hertzfrequenzanalyse  DOMINO light - Kardio\Kardio_Analyse
        #   Akzeleration = 1
        #   Dezeleration = 2
        #   Arrhythmie = 3
        #   Tachykardie (breiter QRS Komplex) = 7
        #   Tachykardie (schmaler QRS Komplex) = 8
        #   Asystole = 9

        # Hertzfrequenz Analyse AASM DOMINO - KardioUSA\Kardio_Analyse
        #   Tachykardie (breiter QRS-Komplex) = 1
        #   Tachykardie (schmaler QRS Komplex) = 2
        #   Asystole = 3
        #   Arrhythmie = 6

        # Generic Analyse - Generic\generic
        #   Event1 = 0
        #   Event2 = 1
        #   Event3 = 2

        return a

    # def getBaseAnnotation(self) -> "Annotation":
    #     nameMap = {
    #         "Schlafprofil": "NeuroAdultAASMStaging",
    #         "Flow Analyse": "Apnea",
    #     }
    #     name = nameMap[self.name]
    #     baseAnnotation = Annotation.createAnnotation(name)
    #     baseAnnotation.values = self.values

    #     return baseAnnotation

    @staticmethod
    def fromBaseAnnotation(a) -> "DominoAnnotation":
        da = DominoAnnotation.createAnnotation(a.name)
        da.values = a.values

        return da

    @classmethod
    def fromDataAnnotation(cls, dataAnnotation: RecordAnnotation) -> "DominoAnnotation":
        baseAnnotation = Annotation.fromDataAnnotation(dataAnnotation)
        return cls.fromBaseAnnotation(baseAnnotation)


@classLogger
class DominoAnnotationWriter(RecordWriter, TSMRecordManager):

    lineEnding = "\n"
    annotation = DominoAnnotation

    def writerRecord(recordName):
        raise Exception("only Annotations are supported for Domino at the moment")

    def __init__(self) -> None:
        TSMRecordManager.__init__(self)
        self.xml = None
        self.patient = None

    def saveAnnotation(self, path, filename=""):
        for name, lines in self.annotationFiles.items():
            filename = "%s/%s.txt" % (path, name)
            with io.open(filename, "w", encoding="utf8") as f:
                f.write(self.lineEnding.join(lines) + self.lineEnding)

    def loadBaseAnnotationFile(self):
        self.annotationFiles = {}

        self.fileLines = []

    def addHeader(self, field, value):
        line = "%s: %s" % (field, value)
        self.fileLines.append(line)

    def addValue(self, value, time):
        line = "%s,000;%s" % (time, value)
        self.fileLines.append(line)

    def writeAnnotation(self, annotation: DominoAnnotation):
        self.fileLines = []

        self.addHeader("Signal ID", annotation.id)
        self.addHeader("Start Time", "19.11.2020 19:30:30")
        self.addHeader("Unit", annotation.unit)
        self.addHeader("Signal Type", annotation.signalType)
        self.addHeader("Events list", ",".join(annotation.possibleValues))

        if annotation.rate is not None:
            self.addHeader("Rate", annotation.rate)

        self.fileLines.append("")

        for ev in annotation.values:
            if ev.name != annotation.ignoreValue:
                valueIndex = annotation.valueMapIndex[ev.name]
                time = self.record.start + timedelta(seconds=ev.start)
                self.addValue(valueIndex, time)

        self.annotationFiles[annotation.fileName] = self.fileLines
