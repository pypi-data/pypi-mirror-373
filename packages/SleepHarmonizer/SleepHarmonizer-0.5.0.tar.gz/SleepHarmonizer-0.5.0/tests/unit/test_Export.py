from unittest.mock import patch

import numpy as np
from pyPhases.test.Mocks import OverwriteConfig
from pyPhases.test.TestCase import TestCase
from pyPhasesRecordloader import RecordSignal, Event, Signal

from SleepHarmonizer.phases.Export import Export


def getTestSignalData(i):
    record = RecordSignal(recordId="myId")
    testSignal = Signal(name="testsignal", signal=np.array([1, 2, 3]), frequency=1)
    record.addSignal(signal=testSignal)

    testSignal = Signal(name="testsignalNotTarget", signal=np.array([1, 2, 3]), frequency=1)
    record.addSignal(signal=testSignal)

    events = [Event(start=1, duration=1, name="arousal"), Event(start=1, duration=1, name="arousal_notlisted")]

    return record, events

def getSubjectId(i):
    return i


class TestLoadData(TestCase):
    phase = Export()

    @patch("shutil.move", return_value=None)
    @patch("pyPhasesRecordloaderSHHS.recordLoaders.RecordLoaderSHHS.RecordLoaderSHHS.getSubjectId", side_effect=lambda r: r)
    @patch("pyPhasesRecordloaderSHHS.recordLoaders.RecordLoaderSHHS.RecordLoaderSHHS.getMetaData", return_value={"mydata": "A"})
    @patch("pyPhasesRecordloaderSHHS.recordLoaders.RecordLoaderSHHS.RecordLoaderSHHS.loadRecord", side_effect=getTestSignalData)
    @patch("SleepHarmonizer.recordwriter.RecordWriterEDF.RecordWriterEDF.writeSignals", return_value=None)
    @OverwriteConfig({"recordId": "myId"})
    def testExport(self, mock_writeSignals, mock_loadRecord, metadata_mock, mock_subjectid, mock_move):
        self.phase.run()

        self.assertTrue(mock_writeSignals.called)
        self.assertTrue(mock_loadRecord.called)

        file = mock_writeSignals.call_args[0][0]
        signals = mock_writeSignals.call_args[0][1]
        recordEvents = list(mock_writeSignals.call_args[0][2])

        self.assertEqual(file, "myId-tmp")
        self.assertEqual(len(signals), 1)
        self.assertEqual(len(recordEvents), 1)
        self.assertEqual(signals[0].name, "testsignal")
        self.assertEqual(recordEvents[0]["name"], "arousal")
        self.assertEqual(recordEvents[0]["start"], 1)
        self.assertEqual(recordEvents[0]["duration"], 1)
        self.assertEqual(signals[0].signal.tolist(), [1, 2, 3])
