# import contextlib
# from unittest.mock import MagicMock
# import numpy as np
# import numpy.testing as npt
# from pyPhases.test.Mocks import OverwriteConfig
# from pyPhases.test.TestCase import TestCase
# from pyPhasesRecordloader import RecordSignal, Signal, RecordLoader, SignalPreprocessing

# from SleePyPhases.phases.Eval import Eval



# class TestEval(TestCase):
#     phase = Eval()

#     C1 = np.array([1, 2, 3, 4, 5])
#     C2 = np.array([6, 7, 8, 9, 10])
#     C3 = C2

#     # def config(self):
#     #     return   eventEval
#     # :
#     # manipulationAfterPredict: # postprocessing
#     # - name: deleteIgnoredMultiClass
#     # - name: reduceY
#     #   factor: 750
#     #   reduce: max}

#     def setUp(self):
#         super().setUp()

#         class MyPreprocessing(SignalPreprocessing):
#             def add1(signal: Signal, recordSignal: RecordSignal, config: dict):
#                 signal.signal += 1

#         self.preprocessing = MyPreprocessing(self.getConfig("preprocessing"))

#         dataProcessed = np.array(
#             [
#                 self.C1.reshape(-1, 1),
#                 self.C2.reshape(-1, 1),
#             ]
#         )

#         dataFeatures = np.array(
#             [
#                 np.array([0, 0, 1, 1, 0]).reshape(-1, 1),
#                 np.array([0, 1, 0, 0, 0]).reshape(-1, 1),
#             ]
#         )
#         self.project.registerData("metadata", [{"recordId": str(r)} for r in range(10)])
#         RecordLoader.getRecordList = MagicMock(return_value=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

#         self.project.setConfig("datasetSplit", "test")
#         self.project.registerData("data-processed", dataProcessed)
#         self.project.registerData("data-features", dataFeatures)

#         self.project.setConfig("datasetSplit", "training")
#         self.project.registerData("data-processed", dataProcessed + 1)
#         self.project.registerData("data-features", dataFeatures + 1)

#         self.project.setConfig("datasetSplit", "validation")
#         self.project.registerData("data-processed", dataProcessed + 2)
#         self.project.registerData("data-features", dataFeatures + 2)

#     @OverwriteConfig({"datasetSplit": "test"})
#     def testDataTest(self):
#         data = iter(self.getData("dataset-test"))

#         x, y = data.__next__()
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 1, 2, 3, 4, 5, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 0, 1, 1, 0, -1, -1])

#         x, y = data.__next__()
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 6, 7, 8, 9, 10, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 0, 1, 0, 0, 0, -1, -1])

#     @OverwriteConfig({"datasetSplit": "training"})
#     def testDataTraining(self):
#         data = iter(self.getData("dataset-training"))

#         x, y = data.__next__()
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 2, 3, 4, 5, 6, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 1, 1, 2, 2, 1, -1, -1])

#         x, y = data.__next__()
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 7, 8, 9, 10, 11, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 1, 2, 1, 1, 1, -1, -1])

#     @OverwriteConfig({"datasetSplit": "validation"})
#     def testDataValidation(self):
#         data = iter(self.getData("dataset-validation"))

#         x, y = data.__next__()
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 3, 4, 5, 6, 7, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 2, 2, 3, 3, 2, -1, -1])

#         x, y = data.__next__()
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 8, 9, 10, 11, 12, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 2, 3, 2, 2, 2, -1, -1])

#     @OverwriteConfig({"BuildDataset": {"useMultiThreading": True, "threads": 2}, "datasetSplit": "validation"})
#     def testMultiThreading(self):
#         with contextlib.suppress(KeyError):
#             self.project.unregister("dataset-validation")
#         data = self.getData("dataset-validation")
#         datagen = iter(data)
#         x, y = next(datagen)
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 3, 4, 5, 6, 7, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 2, 2, 3, 3, 2, -1, -1])

#         x, y = next(datagen)
#         npt.assert_equal(x.reshape(-1), [0, 0, 0, 8, 9, 10, 11, 12, 0, 0])
#         npt.assert_equal(y.reshape(-1), [-1, -1, -1, 2, 3, 2, 2, 2, -1, -1])
