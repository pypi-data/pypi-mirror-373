import unittest
from SleePyPhases.SignalPreprocessing import SignalPreprocessing
from pyPhasesRecordloader import RecordSignal, Signal
import numpy as np

class TestSignalPreprocessing(unittest.TestCase):

    def setUp(self):
        self.preprocessor = SignalPreprocessing({"stepsPerType": {}})

        recordSignal = RecordSignal("test_record", 100)
        recordSignal.addSignal(Signal("ch1", np.random.randn(100), frequency=100))
        recordSignal.addSignal(Signal("ch2", np.random.randn(100), frequency=100))
        self.recordSignal = recordSignal

    def test_rls(self):
        
        signal = Signal("test", np.random.randn(100), frequency=100)

        self.preprocessor.rls(signal, self.recordSignal, ["ch1", "ch2"], [])
        
        self.assertIsInstance(signal.signal, np.ndarray)
        self.assertEqual(signal.signal.shape, (100,))
        self.assertFalse(np.any(np.isnan(signal.signal)))

    
    def test_zerophase(self):
        b = np.array([0.1, 0.2, 0.3])
        a = np.array([1.0, -0.3, 0.2])
        x = np.array([1.0, 2.0, 3.0, 4.0])
        
        result = self.preprocessor._zerophase(b, a, x)
        
        # Add your assertions here
        # For example, to check type:
        self.assertIsInstance(result, np.ndarray)
        
        # To check against known values:
        expected_result = np.array([0.60434229, 0.9425683 , 0.535641  , 0.18467   ])  # Replace with the actual expected result
        np.testing.assert_array_almost_equal(result, expected_result, decimal=5)
