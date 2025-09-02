import contextlib
from unittest.mock import MagicMock
import numpy as np
import numpy.testing as npt
import pandas as pd
from pyPhases.test.Mocks import OverwriteConfig
from pyPhases.test.TestCase import TestCase
from pyPhasesRecordloader import RecordSignal, Signal, RecordLoader, SignalPreprocessing
from pyPhasesML.exporter.MemmapRecordExporter import MemmapRecordExporter

from SleePyPhases.phases.BuildDataset import BuildDataset


class TestBuildDatasetSegments(TestCase):
    """ Test Scenario:
        - Dataset with 10 Recordings: training [id 0-3], validation [id 4-6], test [id 7-9]
        - Each Recording just consist of a single channels with incread segment count: [[0], [0, 1], [0, 1, 2], ... , [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]

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
            "recordWise": False,
            "segmentLength": 2,
            "segmentLengthLabel": 1,
            "segmentManipulation": [{"name": "addBatchDimension"}],
            "segmentManipulationEval": [{"name": "addBatchDimension"}],
            # "segmentManipulation": [{"name": "fixedSize", "position": "center", "size": 10}],
            # "segmentManipulationEval": [{"name": "fixedSize", "position": "center", "size": 10}],
            # "evalOn": None,
        }
    
    def _createMemmapRecordExporterFromArray(self, array, name):
        length = sum([sum(a) for a in array])
        lengths = [int(len(a)) for a in array]
        path = f"data/test-{name}.memmap"
        shape = (1, sum(lengths), 1)

        memmap = np.memmap(path, dtype="float16", mode="w+", shape=shape)
        start = 0
        for a in array:
            start = start
            end = start + len(a)
            memmap[0, start:end, 0:1] = a
            start = end
        
        dataMemmap = MemmapRecordExporter()
        dataMemmap.recordLengths = lengths
        dataMemmap.recordLengths_cumulative = np.cumsum([0] + lengths)
        dataMemmap.fileShape = tuple(shape)
        dataMemmap.type = "float16"
        dataMemmap.CurrentItemIndex = 0
        dataMemmap.filePath = path

        return dataMemmap

    def setUp(self):
        super().setUp()

        class MyPreprocessing(SignalPreprocessing):
            def add1(signal: Signal, recordSignal: RecordSignal, config: dict):
                signal.signal += 1

        self.preprocessing = MyPreprocessing(self.getConfig("preprocessing"))

        dataProcessed = [np.arange(2*i).reshape(-1, 1) for i in range(1, 11)]
        dataFeatures = [np.arange(i).reshape(i, 1) for i in range(1, 11)]

        self.project.registerData("metadata", pd.DataFrame([{"recordId": str(r)} for r in range(10)]))
        RecordLoader.getRecordList = MagicMock(return_value=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])


        self.project.registerData("data-processed", self._createMemmapRecordExporterFromArray(dataProcessed, "data-processed"))
        self.project.registerData("data-features", self._createMemmapRecordExporterFromArray(dataFeatures, "data-features"))

        with self.project:
            self.project.config.update({"dataversion": {"split": None}, "validationSplit": 0.4, "testSplit": 0.3})
            self.project.registerData("data-processed", self._createMemmapRecordExporterFromArray(dataProcessed, "data-processed"))
            self.project.registerData("data-features", self._createMemmapRecordExporterFromArray(dataFeatures, "data-features"))

    def _validateRecord(self, index, data):
        for i in range(index + 1):
            x, y = data.__next__()
            npt.assert_equal(x[0, :, 0], [i*2, i*2+1])
            npt.assert_equal(y[0, :, 0], [i])

    
    @OverwriteConfig({"recordWise": True, "dataversion": {"split": None}, "validationSplit": 0.4, "testSplit": 0.3})
    def testRecordOverview(self):
        data = self.getData("dataset-test")
        npt.assert_equal(data[0][0], np.array([0, 1]).reshape(1, -1, 1))
        npt.assert_equal(data[0][1], np.array([0]).reshape(1, -1, 1))
        
        npt.assert_equal(data[1][0], np.array([0, 1, 2, 3]).reshape(1, -1, 1))
        npt.assert_equal(data[1][1], np.array([0, 1]).reshape(1, -1, 1))

        npt.assert_equal(data[2][0], np.array([0, 1, 2, 3, 4, 5]).reshape(1, -1, 1))
        npt.assert_equal(data[2][1], np.array([0, 1, 2]).reshape(1, -1, 1))

        data = self.getData("dataset-validation")

        npt.assert_equal(data[0][0], np.array([0, 1, 2, 3, 4, 5, 6, 7]).reshape(1, -1, 1))
        npt.assert_equal(data[0][1], np.array([0, 1, 2, 3]).reshape(1, -1, 1))
    
        npt.assert_equal(data[1][0], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).reshape(1, -1, 1))
        npt.assert_equal(data[1][1], np.array([0, 1, 2, 3, 4]).reshape(1, -1, 1))

        npt.assert_equal(data[2][0], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]).reshape(1, -1, 1))
        npt.assert_equal(data[2][1], np.array([0, 1, 2, 3, 4, 5]).reshape(1, -1, 1))

        data = self.getData("dataset-training")

        npt.assert_equal(data[0][0], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]).reshape(1, -1, 1))
        npt.assert_equal(data[0][1], np.array([0, 1, 2, 3, 4, 5, 6]).reshape(1, -1, 1))

        npt.assert_equal(data[1][0], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]).reshape(1, -1, 1))
        npt.assert_equal(data[1][1], np.array([0, 1, 2, 3, 4, 5, 6, 7]).reshape(1, -1, 1))

        npt.assert_equal(data[2][0], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]).reshape(1, -1, 1))
        npt.assert_equal(data[2][1], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8]).reshape(1, -1, 1))

        npt.assert_equal(data[3][0], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]).reshape(1, -1, 1))
        npt.assert_equal(data[3][1], np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).reshape(1, -1, 1))
    

    def testDataTraining(self):
        data = self.getData("dataset-training")

        # segmentCount: 1 + 2 + 3 + 4 = 10
        self.assertEqual(len(data), 10)
        dataIter = iter(data)

        self._validateRecord(0, dataIter)
        self._validateRecord(1, dataIter)
        self._validateRecord(2, dataIter)
        self._validateRecord(3, dataIter)

    def testDataValidation(self):
        data = self.getData("dataset-validation")

        # segmentCount: 5 + 6 + 7 = 18
        self.assertEqual(len(data), 18)
        dataIter = iter(data)

        self._validateRecord(4, dataIter)
        self._validateRecord(5, dataIter)
        self._validateRecord(6, dataIter)

    def testDataTest(self):
        data = self.getData("dataset-test")

        # segmentCount: 8 + 9 + 10 = 27
        self.assertEqual(len(data), 27)
        dataIter = iter(data)

        self._validateRecord(7, dataIter)
        self._validateRecord(8, dataIter)
        self._validateRecord(9, dataIter)


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

    
    @OverwriteConfig({"dataversion": {"split": None}, "validationSplit": 0.4, "testSplit": 0.3})
    def testSingleSegment(self):
        data = self.getData("dataset-test")

        # first segment (record 0 segment 0)
        X, Y = data[0]
        npt.assert_equal(X[0], np.array([0, 1]).reshape(-1, 1))
        npt.assert_equal(Y[0], np.array([0]).reshape(-1, 1))

        # 3nd segment (record 1 segment 1)
        X, Y = data[1]
        npt.assert_equal(X[0], np.array([0, 1]).reshape(-1, 1))
        npt.assert_equal(Y[0], np.array([0]).reshape(-1, 1))

        # 4th segment (record 1 segment 2)
        X, Y = data[2]
        npt.assert_equal(X[0], np.array([2, 3]).reshape(-1, 1))
        npt.assert_equal(Y[0], np.array([1]).reshape(-1, 1))

        # 8th segment (record 3 segment 1)
        X, Y = data[5]
        npt.assert_equal(X[0], np.array([4, 5]).reshape(-1, 1))
        npt.assert_equal(Y[0], np.array([2]).reshape(-1, 1))

    @OverwriteConfig({"dataversion": {"split": None}, "validationSplit": 0.4, "testSplit": 0.3})
    def testAutoSplit(self):
        with contextlib.suppress(KeyError):
            self.project.unregister("dataset-training")
            self.project.unregister("dataset-validation")
            self.project.unregister("dataset-test")

            
        data = self.getData("dataset-test")

        # segmentCount: 1 + 2 + 3 = 6
        self.assertEqual(len(data), 6)
        dataIter = iter(data)

        self._validateRecord(0, dataIter)
        self._validateRecord(1, dataIter)
        self._validateRecord(2, dataIter)

        data = self.getData("dataset-validation")

        # segmentCount: 4 + 5 + 6 = 15
        self.assertEqual(len(data), 15)
        dataIter = iter(data)

        self._validateRecord(3, dataIter)
        self._validateRecord(4, dataIter)
        self._validateRecord(5, dataIter)
        
        data = self.getData("dataset-training")

        # segmentCount: 7 + 8 + 9 + 10 = 34
        self.assertEqual(len(data), 34)
        dataIter = iter(data)

        self._validateRecord(6, dataIter)
        self._validateRecord(7, dataIter)
        self._validateRecord(8, dataIter)
        self._validateRecord(9, dataIter)