
from abc import ABC, abstractmethod
import datetime
from pathlib import Path
from typing import List
from pyPhases.util.Logger import classLogger
from pyPhasesRecordloader.Event import Event
from pyPhasesRecordloader.RecordSignal import Signal
from pyPhasesRecordloader.util.DynamicModule import DynamicModule

import SleepHarmonizer.recordwriter as recordManagerPath


@classLogger
class RecordWriter(ABC):
    recordWriter = DynamicModule(recordManagerPath)

    recordWriters = {
        "RecordWriterEDF": "SleepHarmonizer.recordwriter",
        "RecordWriterDICOM": "SleepHarmonizer.recordwriter",
    }

    @classmethod
    def get(cls) -> "RecordWriter":
        packageName = cls.recordWriters[cls.recordWriter.moduleName]
        return cls.recordWriter.get(packageName)

    def __init__(self, filePath = ".") -> None:
        self.filePath = filePath
        self.metaData = {}

        
    def getFilePath(self, recordName):
        return f"{self.filePath}/{recordName}"

    
    def createFolderStructure(self):
        p = Path(self.filePath)
        p.parent.mkdir(parents=True, exist_ok=True)

    def exist(self, recordName):
        return Path(self.getFilePath(recordName)).exists()
    
    @abstractmethod
    def writeSignals(self, recordName, channels: List[Signal], events: List[Event]=None, startTime: datetime = None, signalIsDigital=False, force=False):
        pass
        
