import unittest

import numpy as np
import numpy.testing as npt
from numpy.random import default_rng
from pyPhases import classLogger

from SleePyPhases.DataManipulation import DataManipulation


@classLogger
class TestDataManipulation(unittest.TestCase):
    def getDA(self, numLabels=2):
        return DataManipulation.getInstance(
            [],
            "Test",
            {
                "numLabels": numLabels,
                "numClasses": [[2]],
            },
            seed=2,
        )

    def test_combineWithPatience(self):
        da = self.getDA()

        prediction = np.array([0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1])
        expected = np.array([0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1])
        patience = 2
        X = da._combineWithPatience(prediction, patience)

        npt.assert_equal(X, expected)
        
    def test_combineWithPatienceMoreSegments(self):
        da = self.getDA()

        prediction = np.array([0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1])
        expected = np.array([0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1])

        X = da._combineWithPatience(prediction, patience=2)

        npt.assert_equal(X, expected)

    def test_combineWithPatienceMinority2(self):
        da = self.getDA()

        prediction = np.array([0, 1, 0, 0, 0, 1])
        expected = np.array([0, 1, 1, 1, 1, 1])

        X = da._combineWithPatience(prediction, patience=4)

        npt.assert_equal(X, expected)

    def test_combineWithPatienceMulticlassGap(self):
        da = self.getDA()

        prediction = np.array([0, 1, 0, 0, 1, 2, 1, 0, 0, 1, 1])
        expected = np.array([0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1])
        patience = 2
        X = da._combineWithPatience(prediction, patience)

        npt.assert_equal(X, expected)
        
    def test_combineWithPatienceMulticlassEnd(self):
        da = self.getDA()

        prediction = np.array([0, 1, 0, 0, 2, 2, 1, 0, 0, 1, 1])
        expected = np.array([0, 1, 0, 0, 2, 2, 2, 0, 0, 1, 1])
        patience = 2
        X = da._combineWithPatience(prediction, patience)

        npt.assert_equal(X, expected)
        
    def test_combineWithPatienceMulticlassStart(self):
        da = self.getDA()

        prediction = np.array([0, 1, 0, 0, 1, 2, 2, 0, 0, 1, 1])
        expected = np.array([0, 1, 0, 0, 2, 2, 2, 0, 0, 1, 1])
        patience = 2
        X = da._combineWithPatience(prediction, patience)

        npt.assert_equal(X, expected)

    def test_minLength(self):
        da = self.getDA()

        prediction = np.array([0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1])
        expected = np.array([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        Y = da._minLength(prediction, minLength=2)

        npt.assert_equal(Y, expected)

    def test_toArousal(self):
        da = self.getDA()
        da.threshold = 0.5

        prediction = np.array([0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0]).reshape(1, -1, 1)
        expected = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]).reshape(1, -1, 1)

        X, _ = da.toArousal(prediction, None, patience=2, minLength=3, frequency=1)

        npt.assert_equal(X, expected)

    def test_hotEncode(self):
        da = self.getDA(numLabels=3)
        Y = np.array([[0, 1, 2], [1, 0, 2]])
        expected_output = np.array([[[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 1, 0], [1, 0, 0], [0, 0, 1]]])
        _, Y_encoded = da.hotEncode(None, Y)
        self.assertTrue(np.array_equal(Y_encoded, expected_output))

    def test_znorm(self):
        X = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
        X, _ = self.getDA().znorm(X, None)
        expected_output = np.array(
            [[-1.34164079, -0.4472136, 0.4472136, 1.34164079], [-1.34164079, -0.4472136, 0.4472136, 1.34164079]]
        )
        self.assertTrue(np.allclose(X, expected_output))

    def test_MagScale(self):
        X = np.array([[1, 2, 3, 4], [5, 6, 7, 8]], dtype=np.float32)
        Xscaled, _ = self.getDA().MagScale(X, None)
        rng = default_rng(seed=2)
        scale = 0.8 + rng.random(1, dtype=np.float32) * 0.45
        self.assertTrue(np.allclose(Xscaled, X * scale))

    def test_channelShuffle(self):
        da = self.getDA()
        X = np.array([[1, 2, 3, 4], [5, 6, 7, 8]]).reshape(1, -1, 2)
        XShuffled, _ = da.channelShuffle(X, None, (1, 3))
        self.assertTrue(np.array_equal(XShuffled, X))
        XShuffled, _ = da.channelShuffle(X, None, (1, 3))
        XShuffled, _ = self.getDA().channelShuffle(X, None, (1, 3))

    def test_fixeSizeSingleChannel(self):
        new_size = 7
        fill_value = 1
        position = "center"
        X = np.array(
            [
                [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]],
                [[16, 17, 18], [19, 20, 21], [22, 23, 24], [25, 26, 27], [28, 29, 30]],
            ]
        )
        newX, _ = self.getDA()._fixeSizeSingleChannel(X, new_size, fill_value, position)

        self.assertEqual(newX.shape, (2, 7, 3))
        self.assertTrue(np.allclose(newX[:, 1:-1, :], X))
        self.assertTrue(np.allclose(newX[:, 0, :], newX[:, -1, :]))
        self.assertTrue(np.allclose(newX[:, 0, :], fill_value))

    def setUp(self):
        self.test_X = np.arange(600).reshape((10, 20, 3))
        self.test_Y = np.arange(300).reshape((10, 30, 1))
        self.test_factor = 2
        self.test_channels = [0, 2, 4]

    def test_restoreLength(self):
        length = 16
        _, new_Y = self.getDA().restoreLength(self.test_X, self.test_Y, length)
        self.assertEqual(new_Y.shape[0], self.test_Y.shape[0])
        self.assertEqual(new_Y.shape[1], length)
        self.assertEqual(new_Y.shape[2], self.test_Y.shape[2])
        npt.assert_equal(new_Y, self.test_Y[:, 7:23, :])

    def test_selectChannel(self):
        channel = 1
        new_X, new_Y = self.getDA().selectChannel(self.test_X, self.test_Y, channel)
        self.assertEqual(new_X.shape, (10, 20, 1))
        self.assertEqual(new_Y.shape, (10, 30, 1))
        self.assertTrue(np.array_equal(new_X[:, :, 0], self.test_X[:, :, channel]))
        self.assertTrue(np.array_equal(new_Y, self.test_Y))

    def test_selectChannelRandom(self):
        selectChannels = [0, 1, 3]
        new_X, new_Y = self.getDA().selectChannelRandom(self.test_X, self.test_Y, selectChannels)
        self.assertEqual(new_X.shape, (10, 20, 1))
        self.assertEqual(new_Y.shape, (10, 30, 1))
        self.assertTrue(np.array_equal(new_X, self.test_X[:, :, 2:3]))
        self.assertTrue(np.array_equal(new_Y, self.test_Y))

    def test_changeType(self):
        dtype = np.float64
        new_X, new_Y = self.getDA().changeType(self.test_X, self.test_Y, dtype)
        self.assertEqual(new_X.dtype, dtype)
        self.assertEqual(new_Y.dtype, dtype)
        self.assertTrue(np.array_equal(new_X, self.test_X.astype(dtype)))
        self.assertTrue(np.array_equal(new_Y, self.test_Y.astype(dtype)))

    def test_reduceY(self):
        reductionFactor = 3
        prediction = np.array([0.2, 0.3, 0.5, 0.4, 0.6, 0.7, 0.8, 0.9, 0.1]).reshape(1, -1, 1)
        Y = np.array([0, 0, 1, 1, 1, 1, 0, 1, 1]).reshape(1, -1, 1)
        
        new_X, new_Y = self.getDA().reduceY(prediction, Y, reductionFactor)
        npt.assert_almost_equal(new_X.reshape(-1), np.array([1/3, 1.7/3, 1.8/3]))
        npt.assert_equal(new_Y.reshape(-1), np.array([0, 1, 1]))

    def test_reduce_max(self):
        reductionFactor = 3
        prediction = np.array([0.2, 0.3, 0.5, 0.4, 0.6, 0.7, 0.8, 0.9, 0.1, 0.8, 0.9, 0.1]).reshape(1, -1, 1)
        Y = np.array([0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0]).reshape(1, -1, 1)
        
        new_X, new_Y = self.getDA().reduceY(prediction, Y, reductionFactor, reduce="max")
        npt.assert_almost_equal(new_X.reshape(-1), np.array([0.5, 0.7, 0.9, 0.9]))
        npt.assert_equal(new_Y.reshape(-1), np.array([1, 1, 1, 0]))

    def test_deleteIgnored(self):
        testY = np.array([1, 2, 3, -1, 2, 2, 3, -1, 2, -1, 2]).reshape(1, -1, 1)
        testX = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]).reshape(1, -1, 1)
        newX, newY = self.getDA().deleteIgnored(testX, testY)
        npt.assert_equal(newY.reshape(-1), [1, 2, 3, 2, 2, 3, 2, 2])
        npt.assert_equal(newX.reshape(-1), [1, 2, 3, 5, 6, 7, 9, 11])

    def test_derive_basic(self):
        X = np.arange(1*2*10).reshape(1, 2, 10).transpose(0, 2, 1)
        Y = np.array([0, 1])
        channels = [1, 0]
        X_result, Y_result = self.getDA().derive(X, Y, channels)
        X_expected = np.arange(1*2*10).reshape(1, 2, 10)
        X_expected = np.array([[
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        ]]).transpose(0, 2, 1)
        self.assertTrue(np.array_equal(X_result, X_expected))
        self.assertTrue(np.array_equal(Y_result, Y))

    def test_extendEvents(self):
        da = self.getDA()
        
        # Create test data with a single event
        Y = np.zeros((1, 10, 1))
        Y[0, 4:6, 0] = 1  # Event from index 4 to 5
        X = np.ones_like(Y)  # Dummy X data
        
        # Test extending events by 2 samples before and 1 after
        X_new, Y_new = da.extendEvents(X, Y, channel=0, pre_samples=2, post_samples=1)
        
        # Expected result: Event should now span from index 2 to 6
        expected = np.zeros((1, 10, 1))
        expected[0, 2:7, 0] = 1
        
        npt.assert_equal(Y_new.shape, expected.shape)
        npt.assert_equal(Y_new[0, :, 0], expected[0, :, 0])
        npt.assert_equal(Y_new, expected)
        npt.assert_equal(X_new, X)  # X should remain unchanged

    def test_extendEventsWithIgnoreValues(self):
        da = self.getDA()
        
        # Create test data with a single event
        Y = np.zeros((1, 10, 1))
        Y[0, 0, 0] = -1
        Y[0, -1, 0] = -1

        Y[0, 4:6, 0] = 1  # Event from index 4 to 5
        X = np.ones_like(Y)  # Dummy X data
        
        # Test extending events by 2 samples before and 1 after
        X_new, Y_new = da.extendEvents(X, Y, channel=0, pre_samples=2, post_samples=1)
        
        # Expected result: Event should now span from index 2 to 6
        expected = np.zeros((1, 10, 1))
        expected[0, 0, 0] = -1
        expected[0, -1, 0] = -1
        expected[0, 2:7, 0] = 1
        
        npt.assert_equal(Y_new.shape, expected.shape)
        npt.assert_equal(Y_new[0, :, 0], expected[0, :, 0])
        npt.assert_equal(X_new, X)  # X should remain unchanged
        
    def test_combineY(self):
        da = self.getDA()
        
        X = np.zeros((2, 10, 2))
        Y = np.array([
            [[0], [1], [2], [3], [4], [0], [1], [2], [3], [4]],
            [[4], [3], [2], [1], [0], [4], [3], [2], [1], [0]]
        ])

        # Test combining values 2,1 into 0
        _, Y_out = da.combineY(X, Y.copy(), values=[2, 1, 0])
        expected = np.array([
            [[0], [0], [0], [1], [2], [0], [0], [0], [1], [2]],
            [[2], [1], [0], [0], [0], [2], [1], [0], [0], [0]]
        ])

        np.testing.assert_array_equal(Y_out, expected)
        
        # Test combining values 4,3,2 into 1
        _, Y_out = da.combineY(X, Y.copy(), values=[1, 2])
        expected = np.array([
            [[0], [1], [1], [2], [3], [0], [1], [1], [2], [3]],
            [[3], [2], [1], [1], [0], [3], [2], [1], [1], [0]]
        ])
        np.testing.assert_array_equal(Y_out, expected)