# from unittest import TestCase

# import numpy as np
# from pyPhasesRecordloader import Event

# from SleePyPhases.PSGEventManager import PSGEventManager
# from SleePyPhases.RecordFeatureExtraction import RecordFeatureExtraction


# class TestRecordFeatureExtraction(TestCase):
#     def test_sleep_cycle_normal(self):
#         stagesEpochs = np.array([0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4])
#         stagesEpochs = np.repeat(stagesEpochs, 30)
#         stagesSecondSignal = np.repeat(stagesEpochs, 30)
#         events = PSGEventManager().getEventsFromSignal(stagesSecondSignal, ["W", "N1", "N2", "N3", "R"])


#         # Process using both methods
#         new_result = RecordFeatureExtraction(None).SleepCycles(None, events, None)
        
#         expected = {'start': [90, 360, 690], 'stop': [270, 600, 1110]}
#         # expected = calculateCycles(stagesEpochs, 0)
#         assert expected == new_result, "Results do not match"

#     def test_sleep_cycle_shortRem(self):
#         stagesEpochs = np.array([0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4])
#         stagesEpochs = np.repeat(stagesEpochs, 5)

#         stagesSecondSignal = np.repeat(stagesEpochs, 30)
#         events = PSGEventManager().getEventsFromSignal(stagesSecondSignal, ["W", "N1", "N2", "N3", "R"])


#         new_result = RecordFeatureExtraction(None).SleepCycles(None, events, None)

#         expected = {'start': [115], 'stop': [185]}
#         # expected = calculateCycles(stagesEpochs, 0)
#         assert expected == new_result, "Results do not match"

#     def test_sleep_cycle_offset(self):
#         stagesEpochs = np.array([0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4])
#         stagesEpochs = np.repeat(stagesEpochs, 10)
#         stagesSecondSignal = np.repeat(stagesEpochs, 30)
#         events = PSGEventManager().getEventsFromSignal(stagesSecondSignal, ["W", "N1", "N2", "N3", "R"])
#         events.append(Event("lightOff", 100))


#         new_result = RecordFeatureExtraction(None).SleepCycles(None, events, None)

#         expected = {'start': [220, 330], 'stop': [300, 470]}
#         # expected = calculateCycles(stagesEpochs, 100)
#         assert expected == new_result, "Results do not match"
