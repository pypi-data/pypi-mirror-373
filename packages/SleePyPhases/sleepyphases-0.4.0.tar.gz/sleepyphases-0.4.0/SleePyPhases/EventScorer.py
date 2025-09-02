import numpy as np

from pyPhasesML import Scorer
from SleePyPhases.PSGEventManager import PSGEventManager


class EventScorer(Scorer):
    title = "Eventbasiert-Tolerant"

    def __init__(self, numClasses=None, classNames=None, trace=False) -> None:
        super().__init__(numClasses=numClasses, classNames=classNames, trace=trace)
        self.metrics = ["kappa", "accuracy"]
        self.majorityVote = False

    def scoreMetric(self, metricName, truth, prediction):

        if metricName in self.results:
            return self.results[metricName]

        if metricName == "confusion":
            result = self.scoreEventsConfusion(truth, prediction)
            self.results["confusion"] = result
            return result
        else:
            return super().scoreMetric(metricName, truth, prediction)

    def scoreMetrics(self, truth, prediction):
        self.results = {}
        returnMetrics = {}
        for metricName in self.metrics:
            returnMetrics[metricName] = self.scoreMetric(metricName, truth, prediction)

        return returnMetrics

    def scoreEventsConfusion(self, truth, prediction):
        prediction = self.flattenPrediction(prediction, threshold=self.threshold)
        truth = truth.astype(int)
        prediction = prediction.astype(int)

        confusion = np.full((self.numClasses, self.numClasses), 0)

        em = PSGEventManager()
        actualEvents = em.getEventsFromSignal(truth, self.classNames)
        predictedEvents = em.getEventsFromSignal(prediction, self.classNames, ignore=0)

        negativeEvents = [e for e in actualEvents if self.classNames.index(e.name) == 0]
        actualEvents = [e for e in actualEvents if self.classNames.index(e.name) > 0]


        # calculate false negative + true positives
        for ev in actualEvents:
            actualValue = self.classNames.index(ev.name)
            innerConfusion = np.bincount(prediction[ev.start : ev.end()])
            majorPrediction = innerConfusion.argmax()
            truthExist = any(prediction[ev.start : ev.end()] == actualValue)
            isTP = majorPrediction == actualValue if self.majorityVote else truthExist

            if isTP:
                confusion[actualValue][actualValue] += 1
            else:
                confusion[actualValue][majorPrediction] += 1

        # calculate false positives
        for ev in predictedEvents:
            predValue = self.classNames.index(ev.name)
            innerConfusion = np.bincount(truth[ev.start : ev.end()])
            majorOccurence = innerConfusion.argmax()
            truthExist = any(truth[ev.start : ev.end()] == predValue)
            isTP = majorOccurence == predValue if self.majorityVote else truthExist

            # tp only needs to be handled in actual events
            if not isTP:
                confusion[majorOccurence][predValue] += 1

        # calculate true negatives
        # tn = 0
        for ev in negativeEvents:
            predValue = self.classNames.index(ev.name)
            innerConfusion = np.bincount(prediction[ev.start : ev.end()])
            majorOccurence = innerConfusion.argmax()
            truthExist = any(truth[ev.start : ev.end()] == predValue)
            isTN = majorOccurence == predValue if self.majorityVote else truthExist

            # tp only needs to be handled in actual events
            if isTN:
                confusion[0][0] += 1


        return confusion
