from unittest.mock import Mock
import numpy as np

from pyPhasesRecordloader import RecordSignal, Event, ChannelsNotPresent, Signal
from SleePyPhases.PreManipulation import PreManipulation

class TestPreManipulation:

    def setUp(self):

        # Setup equivalent to the 'record_signal' pytest fixture
        self.mock_signal = RecordSignal(targetFrequency=10)
        self.mock_signal.signals = [Signal("test_1", np.arange(1000), frequency=10)]

    def test_discard_records_not_all_sleepstages_valid(self):
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 30),
            Event("N1", 30, 30),
            Event("N2", 60, 30),
            Event("N3", 90, 30),
            Event("R", 120, 30)
        ]
        record_signal = Mock()
        
        result_signal, result_events = pre_manip.discard_records_not_all_sleepstages(record_signal, events)
        assert result_events == events

    def test_discard_records_missing_stage_raises(self):
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 30),
            Event("N1", 30, 30),
            Event("N2", 60, 30),
            # Missing N3
            Event("R", 90, 30)
        ]
        record_signal = Mock()
        
        with pytest.raises(ChannelsNotPresent):
            pre_manip.discard_records_not_all_sleepstages(record_signal, events)

    def test_remove_undefined_events(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 30),
            Event("undefined", 30, 30),
            Event("N1", 60, 30)
        ]
        
        result_signal, result_events = pre_manip.remove_undefined(record_signal, events)
        assert len(result_events) == 2
        assert all(e.name != "undefined" for e in result_events)
        assert result_events[-1].start == 30
        assert (result_signal.signals[0].signal[0:300] == np.arange(1000)[0:300]).all()
        assert (result_signal.signals[0].signal[300:] == np.arange(1000)[600:]).all()

    def test_remove_undefined_events_default(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation([{"name": "test_step"}])
        events = [
            Event("W", 0, 30),
            Event("undefined", 30, 30),
            Event("N1", 60, 30)
        ]
        
        result_signal, result_events = pre_manip.remove_undefined(record_signal, events)
        assert len(result_events) == 2
        assert all(e.name != "undefined" for e in result_events)
        assert result_events[-1].start == 30
        assert (result_signal.signals[0].signal[0:300] == np.arange(1000)[0:300]).all()
        assert (result_signal.signals[0].signal[300:] == np.arange(1000)[600:]).all()

    def test_remove_undefined_events_overlap(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 30),
            Event("arousal_start", 25, 10),
            Event("arousal_big", 25, 5+30+5),
            Event("undefined", 30, 30),
            Event("arousal_end", 55, 15),
            Event("N1", 60, 30)
        ]
        
        result_signal, result_events = pre_manip.remove_undefined(record_signal, events)
        assert all(e.name != "undefined" for e in result_events)
        assert result_events[-1].start == 30
        # start
        assert result_events[1].name == "arousal_start"
        assert result_events[1].start == 25
        assert result_events[1].duration == 5
        # end
        assert result_events[3].name == "arousal_end"
        assert result_events[3].start == 30
        assert result_events[3].duration == 10
        # big
        assert result_events[2].name == "arousal_big"
        assert result_events[2].start == 25
        assert result_events[2].duration == 5+5

        assert (result_signal.signals[0].signal[0:300] == np.arange(1000)[0:300]).all()
        assert (result_signal.signals[0].signal[300:] == np.arange(1000)[600:]).all()

    def test_balance_wake_excessive_wake_evening(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 30),  # Excessive wake
            Event("N1", 30, 3),
            Event("N2", 33, 10)
        ]
        
        result_signal, result_events = pre_manip.balance_wake(record_signal, events)
        # start
        assert result_events[0].name == "W"
        assert result_events[0].start == 0
        assert result_events[0].duration == 10
        
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[200:]).all()

    def test_balance_wake_excessive_wake_morning(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("N1", 0, 10),  # Excessive wake
            Event("N2", 10, 10),
            Event("W", 20, 70)
        ]
        
        result_signal, result_events = pre_manip.balance_wake(record_signal, events)
        # start
        assert result_events[-1].name == "W"
        assert result_events[-1].start == 20
        assert result_events[-1].duration == 10
        
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[0:300]).all()

    def test_balance_wake_excessive_wake_both(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 10),
            Event("N2", 10, 10),
            Event("W", 20, 70)
        ]
        
        result_signal, result_events = pre_manip.balance_wake(record_signal, events)
        # start
        assert result_events[0].name == "N2"

        assert result_events[-1].name == "W"
        assert result_events[-1].start == 10
        assert result_events[-1].duration == 10
        
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[100:300]).all()

    def test_balance_wake_excessive_wake_keepmorning(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 10),
            Event("N2", 10, 10),
            Event("W", 20, 20),
            Event("N3", 40, 10),
            Event("W", 50, 30)
        ]
        
        result_signal, result_events = pre_manip.balance_wake(record_signal, events)
        # start
        assert result_events[0].name == "N2"
        assert result_events[0].start == 0
        assert result_events[0].duration == 10

        assert result_events[-1].name == "N3"
        assert result_events[-1].start == 30
        assert result_events[-1].duration == 10
        
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[100:500]).all()

    
    def test_trim_spt_default(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 40),
            Event("N1", 40, 20),
            Event("W", 60, 40)
        ]
        
        result_signal, result_events = pre_manip.trimSPT(record_signal, events, 30, 30)
        assert len(result_events) > 0
        assert result_events[0].name == "W"
        assert result_events[0].start == 0
        assert result_events[0].duration == 30

        assert result_events[1].name == "N1"
        assert result_events[1].start == 30
        assert result_events[1].duration == 20

        assert result_events[2].name == "W"
        assert result_events[2].start == 50
        assert result_events[2].duration == 30

        assert (result_signal.signals[0].signal[:] == np.arange(1000)[100:900]).all()

    def test_trim_spt_evening_only(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 60),
            Event("N1", 60, 30),
            Event("W", 90, 10)
        ]
        
        result_signal, result_events = pre_manip.trimSPT(record_signal, events, 30, 30)
        assert len(result_events) > 0
        assert result_events[0].name == "W"
        assert result_events[0].start == 0
        assert result_events[0].duration == 30
        assert result_events[1].name == "N1"
        assert result_events[1].start == 30
        assert result_events[1].duration == 30
        assert result_events[2].name == "W"
        assert result_events[2].start == 60
        assert result_events[2].duration == 10

        assert (result_signal.signals[0].signal[:] == np.arange(1000)[300:1000]).all()
    
    def test_trim_spt_morning_only(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 30),
            Event("N1", 30, 30),
            Event("W", 60, 40)
        ]
        
        result_signal, result_events = pre_manip.trimSPT(record_signal, events, 30, 30)
        assert len(result_events) > 0
        assert result_events[0].name == "W"
        assert result_events[0].start == 0
        assert result_events[0].duration == 30
        assert result_events[1].name == "N1"
        assert result_events[1].start == 30
        assert result_events[1].duration == 30
        assert result_events[2].name == "W"
        assert result_events[2].start == 60
        assert result_events[2].duration == 30

        assert (result_signal.signals[0].signal[:] == np.arange(1000)[0:900]).all()
    
    def test_trim_spt_no_morning(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 60),
            Event("N1", 60, 30)
        ]
        
        result_signal, result_events = pre_manip.trimSPT(record_signal, events, 30, 30)
        assert len(result_events) > 0
        assert result_events[0].name == "W"
        assert result_events[0].start == 0
        assert result_events[0].duration == 30
        assert result_events[1].name == "N1"
        assert result_events[1].start == 30
        assert result_events[1].duration == 30

        assert (result_signal.signals[0].signal[:] == np.arange(1000)[300:900]).all()
        
    def test_step_invalid_name(self, config):
        pre_manip = PreManipulation({})
        with pytest.raises(Exception) as exc:
            pre_manip.step("invalid_step", Mock(), [])
        assert "PreManipulation 'invalid_step' not found" in str(exc.value)


    def test_trim_to_light_and_scoring(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 0, 20),
            Event("lightOff", 10, 0),
            Event("N1", 20, 30),
            Event("N2", 50, 20),
            Event("lightOn", 80, 0),
            Event("W", 70, 20)
        ]

        result_signal, result_events = pre_manip.trimToLightAndScoring(record_signal, events)

        # Check if trimming is done correctly based on light events
        assert result_events[0].start == 0  # Events should start at 0 after trimming
        assert len(result_events) == 4  # light events removed

        # Verify signal trimming
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[100:800]).all()


    def test_trim_to_light_and_scoring_no_light_events(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 10, 20),
            Event("N1", 30, 30),
            Event("N2", 60, 20),
            Event("W", 80, 20)
        ]
        
        result_signal, result_events = pre_manip.trimToLightAndScoring(record_signal, events)
        
        assert result_events[0].start == 0  # First event should start at 0
        assert result_events[1].start == 20  # First event should start at 0
        assert result_events[2].start == 50  # First event should start at 0
        assert result_events[3].start == 70  # First event should start at 0
        assert len(result_events) == 4  # Should keep all sleep stages
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[100:1000]).all()

    def test_trim_to_light_and_scoring_only_light_off(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("lightOff", 10, 0),
            Event("W", 20, 20),
            Event("N1", 40, 30),
            Event("N2", 70, 20),
            Event("W", 90, 20)
        ]
        
        result_signal, result_events = pre_manip.trimToLightAndScoring(record_signal, events)
        
        assert result_events[0].name == "W"
        assert result_events[0].start == 0
        assert result_events[0].duration == 20
        assert result_events[1].start == 20
        assert result_events[2].start == 50
        assert result_events[3].start == 70
        assert len(result_events) == 4
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[200:]).all()

    def test_trim_to_scoring_with_arousals(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("arousal", 0, 5),
            Event("arousal", 7, 3),
            Event("W", 10, 20),
            Event("N1", 30, 30),
            Event("N2", 60, 20),
            Event("arousal", 70, 10),
            Event("W", 80, 20)
        ]
        
        result_signal, result_events = pre_manip.trimToLightAndScoring(record_signal, events)
        
        assert result_events[0].start == 0
        assert result_events[0].name == "W"
        assert len(result_events) == 5  # Should keep all events including arousal
        assert next(e for e in result_events if e.name == "arousal").start == 60  # Arousal timing adjusted
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[100:1000]).all()
    
    def test_trim_to_light_and_scoring_with_arousals(self):
        record_signal = self.mock_signal
        pre_manip = PreManipulation({})
        events = [
            Event("W", 10, 20),
            Event("N1", 30, 30),
            Event("N2", 60, 20),
            Event("arousal", 70, 10),
            Event("W", 80, 20)
        ]
        
        result_signal, result_events = pre_manip.trimToLightAndScoring(record_signal, events)
        
        assert result_events[0].start == 0
        assert len(result_events) == 5  # Should keep all events including arousal
        assert next(e for e in result_events if e.name == "arousal").start == 60  # Arousal timing adjusted
        assert (result_signal.signals[0].signal[:] == np.arange(1000)[100:1000]).all()