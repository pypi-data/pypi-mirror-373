import numpy as np
from pyPhases.test.Mocks import OverwriteConfig
from pyPhases.test.TestCase import TestCase
from pyPhasesML import DataversionManager

from SleePyPhases.phases.Setup import Setup


class TestSetup(TestCase):
    phase = Setup()
    
    def config(self):
        self.project.setConfig("dataversion.split", {})
        return {
            "fold": 0,
            "validationSplit": 0.25,
            "dataversion": {
                "seed": None,
                "split": {
                    "trainvaltest": ["0:10"],
                },
                "folds": 5,
                "groupBy": None,
                "recordIds": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            },
        }
    
    def testConfigValues(self):
        self.assertEqual(self.getConfig("numLabels"), 1)
        self.assertEqual(self.getConfig("numClasses"), [2])
        # self.assertEqual(self.getConfig("fold"), 0)
        # self.assertEqual(self.getConfig("datasetSplits"), [])
        # self.assertEqual(self.getConfig("hasFolds"), False)

    # def testDataVersionManagerTestFold(self):

    #     # self.project.setConfig("dataversion.split", {})
    #     # self.project.config.update("dataversion", {"folds": 5, "split": {"trainvaltest": ["0:10"]}})
    #     dm = self.getData("dataversionmanager", DataversionManager)
    #     self.assertEqual(dm.getRecordsForSplit("test"), ["0", "1"])
    #     self.assertEqual(dm.getRecordsForSplit("validation"), ["2", "3"])
    #     self.assertEqual(dm.getRecordsForSplit("training"), ["4", "5", "6", "7", "8"])

    # @OverwriteConfig({"fold": 1})
    # def testDataVersionManagerTestFold1(self):
    #     # self.project.setConfig("dataversion.split", {})
    #     # self.project.config.update("dataversion", {"folds": 5, "split": {"trainvaltest": ["0:10"]}})
        

    #     dm = self.getData("dataversionmanager", DataversionManager)
    #     self.assertEqual(dm.getRecordsForSplit("test"), ["0", "1"])
    #     self.assertEqual(dm.getRecordsForSplit("validation"), ["2", "3"])
    #     self.assertEqual(dm.getRecordsForSplit("training"), ["4", "5", "6", "7", "8"])
