from pathlib import Path
from unittest.mock import patch

import pandas as pd

from pyPhases.test import mockLogger
from pyPhases.test.Mocks import OverwriteConfig
from pyPhases.test.TestCase import TestCase

from SleepHarmonizer.phases.LoadData import LoadData


class TestLoadData(TestCase):
    phase = LoadData()

    def config(self):
        return {"dataversion": {"recordIds": None, "groupBy": None}}
    
    def setUp(self):
        super().setUp()
        dataIds = ["metadata-tmp", "allDBRecordIds"]
        for dId in dataIds:
            dId = self.project.getDataFromName(dId).getDataId()
            Path(f"data/{dId}").unlink(missing_ok=True)
        self.patcher_exists = patch("pathlib.Path.exists", return_value=True)
        self.mock_exists = self.patcher_exists.start()
        
        self.patcher_records = patch("pyPhasesRecordloader.RecordLoader.RecordLoader.getRecordList")
        self.mock_records = self.patcher_records.start()
        
        self.patcher_metadata = patch("pyPhasesRecordloaderSHHS.recordLoaders.RecordLoaderSHHS.RecordLoaderSHHS.getMetaData") 
        self.mock_metadata = self.patcher_metadata.start()    
        
        self.mock_metadataDict = {}
        def get_consistent_metadata(recordId):
            return self.mock_metadataDict.get(recordId, {})
    
        self.mock_metadata.side_effect = get_consistent_metadata

    def tearDown(self):
        self.patcher_exists.stop()
        self.patcher_records.stop() 
        self.patcher_metadata.stop()
        super().tearDown()


    def assert_metadata_equals(self, expected_data):
        metadata = self.project.getData("metadata")
        pd.testing.assert_frame_equal(
            metadata,
            pd.DataFrame(expected_data).set_index("recordId", drop=False),
            check_like=True  # Ignore column order during comparison
        )

    @OverwriteConfig({"dataversion": {"recordIds": ["id1", "id2", "id3"]}})
    def testMainFixedRecordIds(self):
        self.assertDataEqual("allDBRecordIds", {
            "id1": ["id1"], 
            "id2": ["id2"], 
            "id3": ["id3"]
        })

    def testMainRecordloader(self):
        self.mock_records.return_value = ["1", "2", "3"]
        self.mock_metadata.return_value = {}
        
        self.assertDataEqual("allDBRecordIds", {
            "1": ["1"], 
            "2": ["2"], 
            "3": ["3"]
        })

    def test_Metadata(self):
        self.mock_records.return_value = ["1", "2", "3"]
        self.mock_metadataDict = {
            "1": {"mydata": "A"},
            "2": {"mydata": "B"},
            "3": {"mydata": "C"}
        }

        expected = [
            {"recordId": "1", "metaDataExist": True, "annotationExist": True, "mydata": "A"},
            {"recordId": "2", "metaDataExist": True, "annotationExist": True, "mydata": "B"},
            {"recordId": "3", "metaDataExist": True, "annotationExist": True, "mydata": "C"}
        ]
        self.assert_metadata_equals(expected)

    def test_Metadata_Return(self):
        self.mock_records.side_effect = [["1", "2"], ["1", "2", "3"]]
        self.mock_metadataDict = {
            "1": {"mydata": "A"},
            "2": {"mydata": "B"},
            "3": {"mydata": "C"}
        }

        expected_initial = [
            {"recordId": "1", "annotationExist": True, "metaDataExist": True,  "mydata": "A"},
            {"recordId": "2", "annotationExist": True, "metaDataExist": True,  "mydata": "B"}
        ]
        self.assert_metadata_equals(expected_initial)

        self.project.unregister("metadata")
        self.project.unregister("metadata-tmp")

        expected_final = [
            {"recordId": "1", "annotationExist": True,"metaDataExist": True, "mydata": "A"},
            {"recordId": "2", "annotationExist": True,"metaDataExist": True, "mydata": "B"},
            {"recordId": "3", "annotationExist": True,"metaDataExist": True, "mydata": "C"}
        ]
        self.assert_metadata_equals(expected_final)

    def test_Metadata_specific(self):
        self.mock_records.side_effect = [["1", "2"], ["1", "2", "3"]]
        self.mock_metadataDict = {
            "1": {"mydata": "A"},
            "2": {"mydata": "B"},
            "3": {"mydata": "C"}
        }
        expected_record = {"recordId": "2", 'metaDataExist': True, "annotationExist": True, "mydata": "B"}

        x = self.project.getData("metadata", pd.DataFrame, recordId="2")
        self.assertEqual(len(x), 1, "error in generating specific record metadata")
        self.assertEqual(x.iloc[0].to_dict(), expected_record, "error in generating specific record metadata")

        x = self.project.getData("metadata", pd.DataFrame, recordId="2")
        self.assertEqual(len(x), 1, "error in loading specific record metadata")
        self.assertEqual(x.iloc[0].to_dict(), expected_record, "error in loading specific record metadata")

        # self.project.unregister("metadata")
        
        x = self.project.getData("metadata", pd.DataFrame, recordId="2")
        self.assertEqual(len(x), 1, "error in loading specific record metadata, during read")
        self.assertEqual(x.iloc[0].to_dict(), expected_record, "error in loading specific record metadata, during read")

    @OverwriteConfig({"dataversion": {"filterQuery": "score > 80"}})
    def test_filter_queries(self):
        self.mock_records.return_value = ["1", "2", "3"]
        self.mock_metadataDict = {
            "1": {"mydata": "A", "score": 90},
            "2": {"mydata": "B", "score": 85},
            "3": {"mydata": "C", "score": 70}
        }
        
        self.assertDataEqual("allDBRecordIds", {
            "1": ["1"],
            "2": ["2"]
        })

    @OverwriteConfig({"dataversion": {"channelFilterQuery": "type == 'eeg'"}})
    def test_channel_filter(self):
        self.mock_records.return_value = ["1", "2", "3"]
        self.mock_metadataDict = {
            "1": {"channels": [{"signalName": "EEG A1:C2", "type": "eeg"}]},
            "2": {"channels": [{"signalName": "EOG LLeft", "type": "eog"}]},
            "3": {"channels": [{"signalName": "EEG C3:A2", "type": "eeg"}]}
        }

        self.assertDataEqual("allDBRecordIds", {
            "1": ["1"],
            "3": ["3"]
        })

    @OverwriteConfig({"dataversion": {"filterQuery": "score > 80","channelFilterQuery": "type == 'eeg' and frequency >= 200"}})
    def test_combined_filters(self):
        self.mock_records.return_value = ["1", "2", "3", "4"]
        self.mock_metadataDict = {
            "1": {"score": 90, "channels": [{"signalName": "EEG A1:C2", "type": "eeg", "frequency": 250}]},
            "2": {"score": 85, "channels": [{"signalName": "EOG LLeft", "type": "eog", "frequency": 250}]},
            "3": {"score": 70, "channels": [{"signalName": "EEG C3:A2", "type": "eeg", "frequency": 250}]},
            "4": {"score": 70, "channels": [{"signalName": "EEG C3:A2", "type": "eeg", "frequency": 50}]}
        }

        self.assertDataEqual("allDBRecordIds", {
            "1": ["1"]
        })

    def test_MetadataDiffrentCols(self):
        self.mock_records.return_value = ["1", "2", "3"]
        self.mock_metadataDict = {
            "1": {"mydata": "A"},
            "2": {"mydata2": "B"},
            "3": {"mydata": "C"}
        }

        expected = [
            {"recordId": "1", 'metaDataExist': True, "annotationExist": True, "mydata": "A"},
            {"recordId": "2", 'metaDataExist': True, "annotationExist": True, "mydata2": "B"},
            {"recordId": "3", 'metaDataExist': True, "annotationExist": True, "mydata": "C"}
        ]
        self.assert_metadata_equals(expected)