from unittest.mock import MagicMock, call, patch, ANY

import numpy as np
import numpy.testing as npt
from pyPhases.test.Mocks import OverwriteConfig
from pyPhases.test.TestCase import TestCase
from pyPhasesRecordloader import Event, RecordSignal, Signal

from SleePyPhases.phases.Extract import Extract, RecordProcessor


class TestExtract(TestCase):
    """ Test Scenario for Extract:
        - Dataset with 10 Recordings [id 0-10]
            - 4 Recordings for training [id 0-3]
            - 3 Recordings for validation [id 4-6]
            - 3 Recordings for test [id 7-9]
    """
    phase = Extract()

    def config(self):
        return {
            "Extract": {
                "useMultiThreading": False,
            },
            "dataversion": {
                "seed": None,
                "split": {
                    "training": ["0:4"],
                    "validation": ["4:7"],
                    "test": ["7:10"],
                },
                "groupBy": None,
                "recordIds": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
            },
            "preprocessing": {
                "targetFrequency": 1,
                "labelFrequency": 1,
                "dtype": "float16",
                "stepsPerType": {"test": ["normalize"]},
                "targetChannels": ["C1", "C2", "C3"],
                "forceGapBetweenEvents": False,
                "cutFirstAndLastWake": False,
                "fillLastSleepstage": False,
                "featureChannels": [],
                "manipulationSteps": []
            },
            "classification": {
                "name": "arousal",
                "labelNames": "Arousal",
                "classNames": [["None", "Arousal"]],
            },
        }

    C1 = np.array([1, 2, 3, 4, 5])
    C2 = np.array([6, 7, 8, 9, 10])
    C3 = C2

    def getTestSignal(self, recordId=0):
        recordSignal = RecordSignal(recordId=recordId)
        c1 = np.array([1, 2, 3, 4, 5])
        c2 = np.array([6, 7, 8, 9, 10])
        events = [Event("arousal_rera", 0, duration=1), Event("arousal", 1, duration=2), Event("N1", 0, duration=10)]
        recordId = int(recordId)
        recordSignal.addSignal(Signal("C1", c1 + recordId, 1, typeStr="test"))
        recordSignal.addSignal(Signal("C2", c2 + recordId, 1))
        recordSignal.addSignal(Signal("C3", c2 + recordId, 1, typeStr="test"))

        return recordSignal, events

    # def testPrepareConfig(self):
    #     self.assertEqual(self.phase.getConfig("datasetSplits"), ["training", "validation", "test"])

    def testRecordProcessor(self):
        recordSignal, events = self.getTestSignal()

        recordLoader = MagicMock()
        recordLoader.loadRecord.return_value = (recordSignal, events)
        extractor = MagicMock()

        eventManager = MagicMock()
        eventManager.getEventSignalFromList.return_value = {"arousal": np.array([0, 1, 2, 3, 4])}
        stepsPerType = {"test": ["S1", "S2"]}
        preprocessingConfig = {
            "targetFrequency": 1,
            "labelFrequency": 1,
            "dtype": "float16",
            "targetChannels": ["C1", "C2", "C3"],
            "stepsPerType": stepsPerType,
            "cutFirstAndLastWake": False,
            "fillLastSleepstage": False,
            "featureChannels": [],
            "manipulationSteps": [],
        }
        signalLength = 5

        recordProcessor = RecordProcessor(
            recordLoader,
            preprocessingConfig,
            extractor,
            eventManager,
            labelChannels=["SleepArousals"],
            project=self.project,
        )
        signalArray, eventSignal = recordProcessor("id1")

        recordLoader.loadRecord.assert_called_once_with("id1")
        extractor.preprocessingSignal.assert_called_once_with(recordSignal)
        eventManager.getEventSignalFromList.assert_called_once_with(
            events,
            signalLength,
            targetFrequency=1,
            forceGapBetweenEvents=False,
        )

        self.assertEqual(recordSignal.targetFrequency, 1)
        npt.assert_equal(signalArray[:, 0], self.C1)
        npt.assert_equal(signalArray[:, 1], self.C2)
        npt.assert_equal(signalArray[:, 2], self.C3)
        npt.assert_equal(eventSignal, np.array([0, 0, 1, 1, 1]).reshape(-1, 1))

    @patch("pyPhasesRecordloader.RecordLoader.RecordLoader.loadRecord")
    def testExtractTraining(self, loadRecord):
        loadRecord.side_effect = lambda recordId: self.getTestSignal(recordId)

        processedDataSignals = self.getData("data-processed")
        processedDataFeatures = self.getData("data-features")

        self.assertEqual(len(processedDataSignals), 10)
        self.assertEqual(len(processedDataFeatures), 10)

        for i, signalArray in enumerate(processedDataSignals):
            # should have all 3 signale (C1, C2, C3)
            # the recordId is added to the signal
            # normalize is the defaul preprocessing step for C1 and C3
            npt.assert_equal(signalArray[:, 0], np.linspace(0, 1, 5))
            npt.assert_equal(signalArray[:, 1], self.C2 + i)
            npt.assert_equal(signalArray[:, 2], np.linspace(0, 1, 5))

        for eventArray in processedDataFeatures:
            # arousal 0-1, arousal_rera 1-3
            npt.assert_equal(eventArray[:, 0], [1.0, 1.0, 1.0, 0.0, 0.0])

    @patch("SleePyPhases.phases.Extract.RecordProcessor.__call__")
    @patch("pyPhasesML.exporter.MemmapRecordExporter.MemmapRecordExporter.saveAndAppendArray")
    @patch("pyPhasesML.exporter.MemmapRecordExporter.MemmapRecordExporter.finishStream")
    @patch("pyPhasesML.exporter.MemmapRecordExporter.MemmapRecordExporter.exists")
    def testMissingChannels(self, exists, finishStream, saveAndAppendArrayMock, recordProcessorMock, ):
        recordProcessorMock.side_effect = [(1, 2), None, (3, 4), (5, 6), (5, 6), None]
        exists.side_effect = [True]
        self.phase.threads = 3
        removed = self.phase.buildFromRecords(["record1", "record2", "record3", "record4", "record5", "record6"], force=True)

        saveAndAppendArrayMock.assert_has_calls(
            [
                call(ANY, (1, 3)),  # X1
                call(ANY, (2, 4)),  # Y1
                call(ANY, (5, 5)),  # X2
                call(ANY, (6, 6)),  # Y2
            ]
        )
        self.assertEqual(removed, ['record2', 'record6'])

    @patch("SleePyPhases.phases.Extract.RecordProcessor.__call__") # processedsignal, eventsignal
    @patch("pyPhasesML.exporter.MemmapRecordExporter.MemmapRecordExporter.saveAndAppendArray")
    @patch("pyPhasesML.exporter.MemmapRecordExporter.MemmapRecordExporter.finishStream")
    @patch("pyPhasesML.exporter.MemmapRecordExporter.MemmapRecordExporter.exists")
    def testMissingChannelsSingleBatch(self, exists, finishStream, saveAndAppendArrayMock, recordProcessorMock):
        exists.side_effect =  [True]
        recordProcessorMock.side_effect = [(1, 2), None, (3, 4), (5, 6), (5, 6), None]
        self.phase.threads = 3
        removed = self.phase.buildFromRecords(["record1", "record2", "record3", "record4", "record5", "record6"], force=True)
        saveAndAppendArrayMock.assert_has_calls(
            [
                call(ANY, (1, 3)),  # X1
                call(ANY, (2, 4)),  # Y1
                call(ANY, (5, 5)),  # X2
                call(ANY, (6, 6)),  # Y2
            ]
        )
        self.assertEqual(removed, ["record2", "record6"])

    # @OverwriteConfig(datasetSplit="training")
    # @patch("SleePyPhases.phases.Extract.Extract.buildFromRecords")
    # def testDataSetManager(self, buildFromRecords):
    #     buildFromRecords.return_value = [1, 2]
    #     # training: 0, 1, 2, 3
    #     # training after removed: 0, 3

    #     self.phase.registerData("removedRecordIndexes", [1, 2])
    #     dm = self.getData("dataversionmanager")
    #     trainingIds = dm.getRecordsForSplit("training")

    #     self.assertDataEqual("removedRecordIndexes", [1, 2])
    #     self.assertEqual(dm.removedRecords["training"], [1, 2])
    #     self.assertEqual(trainingIds, ["0", "3"])
    #     self.project.unregister("removedRecordIndexes")
    #     self.project.unregister("dataversionmanager")
