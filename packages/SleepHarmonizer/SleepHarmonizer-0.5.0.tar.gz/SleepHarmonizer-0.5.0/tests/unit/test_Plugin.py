from unittest import TestCase

from pyPhases import Project

from pyPhasesRecordloader import RecordLoader
from SleepHarmonizer.Plugin import Plugin


class TestPlugin(TestCase):
    def setUp(self):
        self.options = {}
        self.project = Project()
        self.project.config = self.project.loadConfig("SleepHarmonizer/config.yaml")
        self.plugin = Plugin(self.project, self.options)

    def test_project_is_extended(self):
        self.assertIn("Export", self.project.phaseMap)
        self.assertIn("LoadData", self.project.phaseMap)

        loadDataPhase = self.project.getPhase("LoadData")
        exportData = [d.name for d in loadDataPhase.exportData]
        self.assertIn("metadata", exportData)
        self.assertTrue("allDBRecordIds", exportData)

    def test_initPlugin(self):
        self.plugin.initPlugin()
        self.assertIn("RecordLoaderDomino", RecordLoader.recordLoaders.keys())
        self.assertIn("RecordLoaderAlice", RecordLoader.recordLoaders.keys())
