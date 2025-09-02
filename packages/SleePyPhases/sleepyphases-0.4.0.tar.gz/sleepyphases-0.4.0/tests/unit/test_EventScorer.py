import unittest
import numpy as np

from SleePyPhases.EventScorer import EventScorer

class TestEventScorer(unittest.TestCase):

    def test_scoreEventsConfusion(self):
        # Define your test inputs and expected output here
        truth = np.array([0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0])
        prediction = np.array([0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0])

        numClasses = 2
        classNames = ['class1', 'class2']
        eventScorer = EventScorer(numClasses=numClasses, classNames=classNames)

        # Set other parameters if needed, like threshold and majorityVote

        # Call the method to be tested
        confusion_matrix = eventScorer.scoreEventsConfusion(truth, prediction)

        # Define the expected confusion matrix based on your inputs
        expected_confusion = np.array([
            [3, 0],
            [0, 2],
        ])

        # Compare the result with the expected value
        np.testing.assert_array_equal(confusion_matrix, expected_confusion)
    
    def test_scoreEventsConfusionFN(self):
        # Define your test inputs and expected output here
        truth =      np.array([0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1])
        prediction = np.array([0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0])

        numClasses = 2
        classNames = ['class1', 'class2']
        eventScorer = EventScorer(numClasses=numClasses, classNames=classNames)

        # Set other parameters if needed, like threshold and majorityVote

        # Call the method to be tested
        confusion_matrix = eventScorer.scoreEventsConfusion(truth, prediction)

        # Define the expected confusion matrix based on your inputs
        expected_confusion = np.array([
            [3, 0],
            [1, 2],
        ])

        # Compare the result with the expected value
        np.testing.assert_array_equal(confusion_matrix, expected_confusion)

    def test_scoreEventsConfusion_majority(self):
        # Define your test inputs and expected output here
        truth =      np.array([0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0])
        prediction = np.array([0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0])

        numClasses = 2
        classNames = ['class1', 'class2']
        eventScorer = EventScorer(numClasses=numClasses, classNames=classNames)
        eventScorer.majorityVote = True

        # Set other parameters if needed, like threshold and majorityVote

        # Call the method to be tested
        confusion_matrix = eventScorer.scoreEventsConfusion(truth, prediction)

        # Define the expected confusion matrix based on your inputs
        expected_confusion = np.array([
            [3, 0],
            [1, 1],
        ])

        # Compare the result with the expected value
        np.testing.assert_array_equal(confusion_matrix, expected_confusion)
    
    # def test_scoreEventsConfusionFN_majority(self):
    #     # Define your test inputs and expected output here
    #     truth = np.array([0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1])
    #     prediction = np.array([0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0])  # Values beyond 4 will be ignored

    #     numClasses = 2
    #     classNames = ['class1', 'class2']
    #     eventScorer = EventScorer(numClasses=numClasses, classNames=classNames)
    #     eventScorer.majorityVote = True

    #     # Set other parameters if needed, like threshold and majorityVote

    #     # Call the method to be tested
    #     confusion_matrix = eventScorer.scoreEventsConfusion(truth, prediction)

    #     # Define the expected confusion matrix based on your inputs
    #     expected_confusion = np.array([
    #         [3, 0],
    #         [1, 2],
    #     ])

    #     # Compare the result with the expected value
    #     np.testing.assert_array_equal(confusion_matrix, expected_confusion)

    # # def test_scoreEventsConfusion(self):
    # #     truth = np.array([0, 0, 1, 1, 0, 1, 0, 1, 0])
    # #     prediction = np.array([0, 1, 1, 0, 0, 1, 1, 0, 0])

    # #     (tn, fn), (fp, tp) = EventScorer(numClasses=2).scoreEventsConfusion(truth, prediction)
    # #     self.assertEqual(tn, 4)
    # #     self.assertEqual(fn, 1)
    # #     self.assertEqual(fp, 0)
    # #     self.assertEqual(tp, 2)

    # # def test_scoreMetrics(self):
    # #     truth = np.array([0, 0, 1, 1, 0, 1, 0, 1, 0])
    # #     prediction = np.array([0, 1, 1, 0, 0, 1, 1, 0, 0])

    # #     metrics = EventScorer(numClasses=2).scoreMetrics(truth, prediction)
    # #     self.assertEqual(metrics["kappa"], 0.696)
    # #     self.assertEqual(metrics["accuracy"], 0.857)
