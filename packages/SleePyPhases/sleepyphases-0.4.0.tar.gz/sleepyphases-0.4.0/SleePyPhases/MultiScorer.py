import numpy as np
from pyPhasesML.scorer.Scorer import Scorer

class MultiScorer(Scorer):
    def __init__(self, numClasses, metrics, scorerNames=[], ignoreClasses=None, classNames=None, scorerClasses=None) -> None:

        ignoreClasses = ignoreClasses or [-1]

        self.scorer = {}
        self.metrics = []
        self.numClasses = len(numClasses)
        self.multiClassNums = numClasses
        self.scorerNames = scorerNames
        self.metricDefinitions = {}

        metrics = metrics if isinstance(metrics[0], list) else [metrics for _ in range(len(numClasses))]

        for i, (numClasses, scorerName) in enumerate(zip(numClasses, scorerNames)):
            scorerClass = scorerClasses[i] if scorerClasses is not None else Scorer
            s = scorerClass(numClasses)
            s.trace = True
            s.ignoreClasses = ignoreClasses
            s.numClasses = numClasses if numClasses > 1 else 2
            s.metrics = metrics[i]
            s.classNames = classNames[i] if classNames is not None else list(range(s.numClasses))
            self.scorer[scorerName] = s
            self.metrics += [f"{m}_{scorerName}" for m in s.metrics]
            self.metricDefinitions.update({f"{m}_{scorerName}": s.getMetricDefinition(m) for m in s.metrics})
            self.metricDefinitions.update({f"{m}": s.getMetricDefinition(m) for m in s.metrics})

    def getMetricDefinition(self, name):
        return self.metricDefinitions[name]
    
    def setThresholds(self, thresholds):
        for s, t in zip(self.scorer.values(), thresholds):
            s.threshold = t

    def score(self, truth, predictions, trace=False):
        # for i, (scorer, classCount) in enumerate(zip(self.scorer.values(), self.multiClassNums)):
        results = {}
        for i, (name, scorer) in enumerate(self.scorer.items()):
            if isinstance(predictions, list) or isinstance(predictions, tuple):
                p = predictions[i]
            elif predictions.shape[-1] == len(self.multiClassNums):
                if len(predictions.shape) == 3:
                    predictions = predictions.reshape(-1, predictions.shape[-1])
                p = predictions[:, i]
            else:
                start = sum(self.multiClassNums[:i])
                end = start + self.multiClassNums[i]
                if len(predictions.shape) == 3:
                    predictions = predictions.reshape(-1, predictions.shape[-1])
                p = predictions[:, start:end]
            
            if isinstance(truth, list) or isinstance(truth, tuple):
                t = truth[i]
            elif truth.shape[-1] == len(self.multiClassNums):
                if len(truth.shape) == 3:
                    truth = truth.reshape(-1, truth.shape[-1])
                t = truth[:, i]
            else:
                start = sum(self.multiClassNums[:i])
                end = start + self.multiClassNums[i]
                if len(truth.shape) == 3:
                    truth = truth.reshape(-1, truth.shape[-1])
                t = truth[:, start:end]

            
            r = scorer.score(t, p, trace=trace)
            results.update({f"{m}_{name}": v for m, v in r.items()})
        return results
    
    def scoreSingle(self, scorerIndex, truth, prediction, trace=False):

        name = self.scorerNames[scorerIndex]
        scorer = self.scorer[name]

        # prepare the prediction/truth:
        #   if it is a list, we assume each label is in a different list
        #   if it is a ND array, we assume the last dimension is the label
        start = sum(self.multiClassNums[:scorerIndex])
        end = start + self.multiClassNums[scorerIndex]        
        if isinstance(prediction, list):
            prediction = np.concatenate([p[:, :] for p in prediction[start:end]], axis=0)
        elif len(prediction.shape) == 3:
            prediction = prediction.reshape(-1, prediction.shape[2])[:, start:end]
        else:
            prediction = prediction[:, start:end]
   
        if isinstance(truth, list):
            truth = truth[scorerIndex]
        elif len(truth.shape) == 3:
            truth = truth.reshape(-1, truth.shape[2])[:, scorerIndex]
        else:
            truth = truth[:, scorerIndex]

        return scorer.score(truth, prediction, trace=trace)
    
    def prettyPrintConfusionMatrix(self, confusion_matrix):
        num_rows, num_cols = confusion_matrix.shape
        max_value_length = max(len(str(confusion_matrix.max())), len(str(confusion_matrix.min())))
        separator = "-" * ((max_value_length + 2) * num_cols)

        rows = []
        for i in range(num_rows):
            row_data = [f"{int(confusion_matrix[i, j]):>{max_value_length}}" for j in range(num_cols)]
            rows.append(" | ".join(row_data))

        print(separator)
        print("\n".join(rows))
        print(separator)
        
    def scoreAllRecords(self):
        results = {}
        self.recordResult = {}
        for name, s in self.scorer.items():
            r = s.scoreAllRecords()
            results.update({f"{m}_{name}": v for m,v in r.items()})
            if "confusion" in r:
                print(f"######{name}########")
                self.prettyPrintConfusionMatrix(r["confusion"] )
            self.recordResult[name] = s.recordResult
        self.results = results

        return results
