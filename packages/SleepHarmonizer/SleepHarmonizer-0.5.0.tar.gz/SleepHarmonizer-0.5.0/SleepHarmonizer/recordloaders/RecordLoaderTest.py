import numpy as np
from .RecordLoaderAlice import RecordLoaderAlice
from pyPhasesRecordloader import Event, RecordSignal, Signal


class RecordLoaderTest(RecordLoaderAlice):
    config = {}

    def getRecordList(self):
        return [f"record-{i}" for i in range(501)]

    def getMetadata(self, recordName):
        intId = int(recordName[7:])
        patientName = "group" if intId < 10 else recordName

        return {
            "patient": patientName,
            "dataCount": 100,
        }
    
    def exist(self, recordId):
        return True
    
    def existAnnotation(self, recordId):
        return recordId != "record-20"
    
    def getSignalHeaders(self, recordId):
        return [{
            "type": "test",
        }]

    def loadRecord(self, recordName):
        intId = int(recordName[7:])

        recordSignal = RecordSignal()
        recordSignal.addSignal(Signal("test1", np.arange(512) + intId - 10, frequency=1))
        recordSignal.addSignal(Signal("test2", np.arange(512) + intId - 9, frequency=1))
        events = [Event("lightOff", 10), Event("lightOn", 510), Event("R", 0, 512)]
        events.append(Event("arousal", int(10 + intId), 5))
        return recordSignal, events
