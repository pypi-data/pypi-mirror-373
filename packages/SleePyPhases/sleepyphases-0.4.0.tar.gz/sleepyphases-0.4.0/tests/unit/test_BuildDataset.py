import contextlib
from unittest.mock import MagicMock
import numpy as np
import numpy.testing as npt
import pandas as pd
from pyPhases.test.Mocks import OverwriteConfig
from pyPhases.test.TestCase import TestCase
from pyPhasesRecordloader import RecordSignal, Signal, RecordLoader, SignalPreprocessing

from SleePyPhases.phases.BuildDataset import BuildDataset


class TestBuildDataset(TestCase):
    """ Test Scenario:
        - Dataset with 10 Recordings: training [id 0-3], validation [id 4-6], test [id 7-9]
        - Each Recording just consist of 2 channels [[0,1], [2,3], ... , [16,17], [18,19]]
        - DataManipulation: transform each recording to fixed size of 10 (0 padded): [[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]], ...]

    """
    phase = BuildDataset()

    C1 = np.array([1, 2, 3, 4, 5])
    C2 = np.array([6, 7, 8, 9, 10])
    C3 = C2

    def config(self):
        self.project.setConfig("dataversion.split", {})
        return {
            "useLoader": "test",
            "dataversion": {
                "split": {
                    "training": ["0:4"],
                    "validation": ["4:7"],
                    "test": ["7:10"],
                },
                "seed": None,
                "recordIds": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                "groupBy": None,
            },
            "segmentManipulation": [{"name": "addBatchDimension"}, {"name": "fixedSize", "position": "center", "size": 10}],
            "segmentManipulationEval": [{"name": "addBatchDimension"}, {"name": "fixedSize", "position": "center", "size": 10}],
            "evalOn": None,
        }

    def setUp(self):
        super().setUp()

        dataProcessed = np.arange(20).reshape(10, 1, 2)
        dataFeatures = np.arange(10).reshape(10, 1, 1)

        self.project.registerData("metadata", pd.DataFrame([{"recordId": str(r)} for r in range(10)]))
        RecordLoader.getRecordList = MagicMock(return_value=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

        self.project.registerData("data-processed", dataProcessed)
        self.project.registerData("data-features", dataFeatures)

    def testDataTraining(self):
        data = self.getData("dataset-training")

        self.assertEqual(len(data), 4)
        data = iter(data)

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 0, -1, -1, -1, -1]).reshape(-1, 1))

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 2, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 3, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 1, -1, -1, -1, -1]).reshape(-1, 1))

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 4, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 5, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 2, -1, -1, -1, -1]).reshape(-1, 1))

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 6, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 7, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 3, -1, -1, -1, -1]).reshape(-1, 1))

    def testDataValidation(self):
        data = self.getData("dataset-validation")

        self.assertEqual(len(data), 3)
        data = iter(data)

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 8, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 9, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 4, -1, -1, -1, -1]).reshape(-1, 1))

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 10, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 11, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 5, -1, -1, -1, -1]).reshape(-1, 1))

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 12, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 13, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 6, -1, -1, -1, -1]).reshape(-1, 1))

    def testDataTest(self):
        data = self.getData("dataset-test")

        self.assertEqual(len(data), 3)
        data = iter(data)

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 14, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 15, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 7, -1, -1, -1, -1]).reshape(-1, 1))

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 16, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 17, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 8, -1, -1, -1, -1]).reshape(-1, 1))

        x, y = data.__next__()
        npt.assert_equal(x[0, :, 0], np.array([0, 0, 0, 0, 0, 18, 0, 0, 0, 0]))
        npt.assert_equal(x[0, :, 1], np.array([0, 0, 0, 0, 0, 19, 0, 0, 0, 0]))
        npt.assert_equal(y[0], np.array([-1, -1, -1, -1, -1, 9, -1, -1, -1, -1]).reshape(-1, 1))


    @OverwriteConfig({"BuildDataset": {"useMultiThreading": True, "threads": 2}})
    def testValidationMultiThreading(self):
        with contextlib.suppress(KeyError):
            self.project.unregister("dataset-validation")
        self.testDataValidation()

    @OverwriteConfig({"BuildDataset": {"useMultiThreading": True, "threads": 2}})
    def testTrainingMultiThreading(self):
        with contextlib.suppress(KeyError):
            self.project.unregister("dataset-training")
        self.testDataTraining()
