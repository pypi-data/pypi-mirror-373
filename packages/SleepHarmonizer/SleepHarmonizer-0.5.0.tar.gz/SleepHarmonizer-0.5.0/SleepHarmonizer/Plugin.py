from pyPhases import Data, PluginAdapter, Project
from pyPhasesRecordloader import RecordLoader

from SleepHarmonizer.recordwriter.RecordWriter import RecordWriter

from .phases.Export import Export
from .phases.LoadData import LoadData


class Plugin(PluginAdapter):
    def __init__(self, project: Project, options=None):
        super().__init__(project, options)

        if "LoadData" not in self.project.phaseMap:
            dataDep = [
                Data("metadata", self.project, ["dataBase"]),
                Data("metadata-channels", self.project, ["dataBase"]),
                Data("allDBRecordIds", self.project, ["metadata", "dataversion.recordIds", "dataversion.groupBy"]),
                Data("metadata-tmp", self.project, ["metadata"]),
                Data("metadata-channels-tmp", self.project, ["metadata-channels"]),
            ]
            loadData = LoadData(dataDep)
            project.addPhase(loadData)
        if "Export" not in self.project.phaseMap:
            project.addPhase(Export([]))

    def initPlugin(self):
        RecordLoader.registerRecordLoader("RecordLoaderTest", "SleepHarmonizer.recordloaders")
        RecordLoader.registerRecordLoader("RecordLoaderDomino", "SleepHarmonizer.recordloaders")
        RecordLoader.registerRecordLoader("RecordLoaderAlice", "SleepHarmonizer.recordloaders")

        RecordWriter.recordWriter.set(
            name=self.getConfig("useWriter"),
            options={"filePath": self.getConfig("export-path")},
            dynOptions={},
        )
