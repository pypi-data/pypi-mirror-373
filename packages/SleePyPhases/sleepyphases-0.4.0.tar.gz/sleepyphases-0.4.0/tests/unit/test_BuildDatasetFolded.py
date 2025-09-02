from unittest.mock import MagicMock

import numpy as np
import numpy.testing as npt
import pandas as pd

from SleePyPhases.phases.BuildDataset import BuildDataset
from pyPhases.test.Mocks import OverwriteConfig
from pyPhases.test.TestCase import TestCase
from pyPhasesRecordloader import RecordLoader


class TestBuildDataset(TestCase):
    phase = BuildDataset()

    C1 = np.array([1, 2, 3, 4, 5])
    C2 = np.array([6, 7, 8, 9, 10])
    C3 = C2

    def config(self):
        self.project.setConfig("dataversion.split", {})
        return {
            "dataversion": {
                "seed": None,
                "split": {
                    "trainval": ["0:8"],
                    "test": ["8:10"],
                },
                "folds": 4,
                "recordIds": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                "groupBy": None,
            },
            "segmentManipulation": [{"name": "addBatchDimension"}, {"name": "fixedSize", "position": "center", "size": 10}],
            "segmentManipulationEval": [{"name": "addBatchDimension"}, {"name": "fixedSize", "position": "center", "size": 10}],
            "evalOn": None,
        }

    def setUp(self):
        super().setUp()

        self.project.registerData("metadata", pd.DataFrame([{"recordId": str(r)} for r in range(10)]))
        RecordLoader.getRecordList = MagicMock(return_value=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        
        self.project.registerData(
            "data-processed",
            np.array([np.arange(5).reshape(-1, 1) + i for i in range(10)]),
        )

        self.project.registerData(
            "data-features",
            np.array(
                [
                    np.array([0, 0, 0, 0, 0]).reshape(-1, 1),
                    np.array([0, 0, 0, 0, 1]).reshape(-1, 1),
                    np.array([0, 0, 0, 1, 0]).reshape(-1, 1),
                    np.array([0, 0, 0, 1, 1]).reshape(-1, 1),
                    np.array([0, 0, 1, 0, 0]).reshape(-1, 1),
                    np.array([0, 0, 1, 0, 1]).reshape(-1, 1),
                    np.array([0, 0, 1, 1, 0]).reshape(-1, 1),
                    np.array([0, 0, 1, 1, 1]).reshape(-1, 1),
                    np.array([0, 1, 0, 0, 0]).reshape(-1, 1),
                    np.array([0, 1, 0, 0, 1]).reshape(-1, 1),
                    # np.array([0, 1, 0, 1, 0]).reshape(-1, 1),
                    # np.array([0, 1, 0, 1, 1]).reshape(-1, 1),
                ]
            )
        )


    def testDataTest(self):
        dataset = self.getData("dataset-test")
        data = iter(dataset)

        self.assertEqual(len(dataset), 2)

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 8, 9, 10, 11, 12, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 1, 0, 0, 0, -1, -1])

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 9, 10, 11, 12, 13, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 1, 0, 0, 1, -1, -1])

    def testDataTraining(self):
        dataset = self.getData("dataset-training")

        self.assertEqual(len(dataset), 6)

        data = iter(dataset)
        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 2, 3, 4, 5, 6, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 1, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 3, 4, 5, 6, 7, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 1, 1, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 4, 5, 6, 7, 8, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 0, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 5, 6, 7, 8, 9, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 0, 1, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 6, 7, 8, 9, 10, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 1, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 7, 8, 9, 10, 11, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 1, 1, -1, -1])

        # x, y = next(data)
        # np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 8, 9, 10, 11, 12, 0, 0])
        # np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 1, 0, 0, 0, -1, -1])

        # x, y = next(data)
        # np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 9, 10, 11, 12, 13, 0, 0])
        # np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 1, 0, 0, 1, -1, -1])

        self.assertRaises(StopIteration, data.__next__)

        data = iter(dataset)
        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 2, 3, 4, 5, 6, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 1, 0, -1, -1])

    @OverwriteConfig(fold=3)
    def testDataTrainingFold3(self):
        data = iter(self.getData("dataset-training"))

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 0, 1, 2, 3, 4, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 0, 0, -1, -1])

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 1, 2, 3, 4, 5, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 0, 1, -1, -1])

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 2, 3, 4, 5, 6, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 1, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 3, 4, 5, 6, 7, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 1, 1, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 4, 5, 6, 7, 8, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 0, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 5, 6, 7, 8, 9, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 0, 1, -1, -1])

        self.assertRaises(StopIteration, data.__next__)

    def testDataValidation(self):
        data = iter(self.getData("dataset-validation"))

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 0, 1, 2, 3, 4, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 0, 0, -1, -1])

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 1, 2, 3, 4, 5, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 0, 1, -1, -1])

        self.assertRaises(StopIteration, data.__next__)

    @OverwriteConfig(fold=1)
    def testDataValidationFold1(self):
        data = iter(self.getData("dataset-validation"))

        x, y = next(data)
        npt.assert_equal(x.reshape(-1), [0, 0, 0, 2, 3, 4, 5, 6, 0, 0])
        npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 1, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 3, 4, 5, 6, 7, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 0, 1, 1, -1, -1])

        self.assertRaises(StopIteration, data.__next__)

    @OverwriteConfig(fold=2)
    def testDataValidationFold2(self):
        data = iter(self.getData("dataset-validation"))

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 4, 5, 6, 7, 8, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 0, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 5, 6, 7, 8, 9, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 0, 1, -1, -1])

        self.assertRaises(StopIteration, data.__next__)

    @OverwriteConfig(fold=3)
    def testDataValidationFold3(self):
        data = iter(self.getData("dataset-validation"))

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 6, 7, 8, 9, 10, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 1, 0, -1, -1])

        x, y = next(data)
        np.testing.assert_equal(x.reshape(-1), [0, 0, 0, 7, 8, 9, 10, 11, 0, 0])
        np.testing.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 1, 1, -1, -1])

        self.assertRaises(StopIteration, data.__next__)
