from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np
import numpy.testing as npt
from pyPhasesRecordloader import Event, RecordSignal, Signal

from SleePyPhases.phases.Extract import RecordProcessor


class TestRecordProcessor(TestCase):
    def getRecordProcessor(self):
        recordLoader = MagicMock()
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
            "extendEvents": {"test": [0, 1]},
        }

        return RecordProcessor(
            recordLoader,
            preprocessingConfig,
            extractor,
            eventManager,
            labelChannels=["SleepArousals"],
        )

    def testCutFirstAndLastWakeStartSPT(self):
        events = [
            Event("arousal", 0, 10),
            Event("W", 30, 30),
            Event("N1", 60, 30),
            Event("arousal", 80, 10),
            Event("arousal", 85, 10),
        ]
        recordProcessor = self.getRecordProcessor()
        rs = RecordSignal(1)
        rs.addSignal(Signal("test", np.arange(100), frequency=1))
        cuttedEvents = recordProcessor.tailorToSleepScoring(rs, events, useSPT=True)

        # self.assertEqual(len(cuttedEvents), 3)
        self.assertEqual(
            cuttedEvents,
            [
                Event("N1", 0, 30),
                Event("arousal", 20, 10),
                Event("arousal", 25, 5),
            ],
        )
        npt.assert_equal(rs.signals[0].signal, np.arange(60, 90))
        
    def testCutFirstAndLastWakeStart(self):
        events = [
            Event("arousal", 0, 10),
            Event("W", 30, 30),
            Event("N1", 60, 30),
            Event("arousal", 80, 10),
            Event("arousal", 85, 10),
        ]
        recordProcessor = self.getRecordProcessor()
        rs = RecordSignal(1)
        rs.addSignal(Signal("test", np.arange(100), frequency=1))
        cuttedEvents = recordProcessor.tailorToSleepScoring(rs, events, useSPT=False)

        # self.assertEqual(len(cuttedEvents), 3)
        self.assertEqual(
            cuttedEvents,
            [
                Event("W", 0, 30),
                Event("N1", 30, 30),
                Event("arousal", 50, 10),
                Event("arousal", 55, 5),
            ],
        )
        npt.assert_equal(rs.signals[0].signal, np.arange(30, 90))

    def testCutFirstAndLastWakeEndSPT(self):
        events = [
            Event("arousal", 65, 5),
            Event("N1", 60, 20),
            Event("W", 80, 30),
            Event("arousal", 80, 40),
        ]
        recordProcessor = self.getRecordProcessor()
        rs = RecordSignal(1)
        rs.addSignal(Signal("test", np.arange(100), frequency=1))

        cuttedEvents = recordProcessor.tailorToSleepScoring(rs, events, useSPT=True)

        self.assertEqual(
            cuttedEvents,
            [
                Event("arousal", 5, 5),
                Event("N1", 0, 20),
            ],
        )
        npt.assert_equal(rs.signals[0].signal, np.arange(60, 80))

    def testCutFirstAndLastWakeEnd(self):
        events = [
            Event("arousal", 65, 5),
            Event("N1", 60, 20),
            Event("W", 80, 30),
            Event("arousal", 80, 40),
        ]
        recordProcessor = self.getRecordProcessor()
        rs = RecordSignal(1)
        rs.addSignal(Signal("test", np.arange(120), frequency=1))
        
        cuttedEvents = recordProcessor.tailorToSleepScoring(rs, events, useSPT=False)

        self.assertEqual(
            cuttedEvents,
            [
                Event("arousal", 5, 5),
                Event("N1", 0, 20),
                Event("W", 20, 30),
                Event("arousal", 20, 30),
            ],
        )
        npt.assert_equal(rs.signals[0].signal, np.arange(60, 110))

    def testLightEvents(self):
        events = [
            Event("arousal", 65, 5),
            Event("lightOff", 75),
            Event("lightOn", 85),
            Event("N1", 60, 20),
            Event("W", 80, 30),
            Event("arousal", 80, 40),
        ]
        recordProcessor = self.getRecordProcessor()
        rs = RecordSignal(1)
        rs.addSignal(Signal("test", np.arange(120), frequency=1))
        
        cuttedEvents = recordProcessor.tailorToSleepScoring(rs, events, useSPT=False)

        self.assertEqual(
            cuttedEvents,
            [
                Event("N1", 0, 5),
                Event("W", 5, 5),
                Event("arousal", 5, 5),
            ],
        )
        npt.assert_equal(rs.signals[0].signal, np.arange(75, 85))
