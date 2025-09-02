import random
import numpy as np
import pandas as pd
from SleePyPhases.MultiScorer import MultiScorer
from pyPhases import Phase
from pyPhasesML import Model, ModelManager, Scorer
from tqdm import tqdm

from SleePyPhases.DataManipulation import DataManipulation
from SleePyPhases.EventScorer import EventScorer
from SleePyPhases.SleepMetaData import SleepMetaData


class Eval(Phase):
    allowTraining: bool = False
    exampleCount: int = 3

    def getModel(self) -> Model:
        modelState = self.project.getData("modelState", Model, generate=self.allowTraining)
        model = ModelManager.getModel(True)
        model.build()
        model.loadState(modelState)
        return model

    def getTestMetadata(self):
        if not bool(self.getConfig("evalOn", {})):
            return self.getData("metadata", list)

        with self.project:
            evalConfig = self.getConfig("evalOn")

            # try not to update dataversion, rather replace it completly
            if "dataversion" in evalConfig:
                self.project.config["dataversion"] = {}

            self.project.config.update(evalConfig)
            self.project.trigger("configChanged", None)
            dm = self.getData("metadata", list)

        return dm

    def getExternalTestset(self):
        with self.project:
            evalConfig = self.getConfig("evalOn")

            # try not to update dataversion, rather replace it completly
            if "dataversion" in evalConfig:
                self.project.config["dataversion"] = {}

            self.project.config.update(evalConfig)
            self.project.trigger("configChanged", None)
            split = self.getConfig("datasetSplit")
            dataset = self.project.getData(f"dataset-{split}", list)
            dm = self.getData("dataversionmanager")
            recordsMap = dm.getRecordsForSplit(split)

            # self.setConfig("datasetSplits", list(self.getConfig("dataversion.split", {}).keys()))
        return dataset, dm, recordsMap

    def getTestDataAndRecordMap(self):
        # load or generate test data and model state
        if bool(self.getConfig("evalOn", {})):
            testData, dm, recordsMap = self.getExternalTestset()
        else:
            testData = self.project.getData("dataset-test", list)
            dm = self.getData("dataversionmanager")
            recordsMap = dm.getRecordsForSplit("test")

        return testData, recordsMap

    def getTestData(self):
        return self.getTestDataAndRecordMap()[0]

    def getTestRecordMap(self):
        return self.getTestDataAndRecordMap()[1]

    def segmentEvaluation(self, name):
        testData = self.getTestData()
        self.setConfig("datasetSplits", list(self.getConfig("dataversion.split", {}).keys()))
        model = self.getModel()

        # setup data and scorer
        
        classNums = self.getConfig("numClasses", [2])
        labelNames = self.getConfig("classification.labelNames")
        ignoreIndex = self.getConfig("classification.ignoreIndex", -1)
        metrics = self.getConfig("trainingParameter.validationMetrics")

        scorer = MultiScorer(classNums, metrics, scorerNames=labelNames, ignoreClasses=[ignoreIndex])
        for s in scorer.scorer.values():
            s.trace = True
        threshold = self.getConfig("fixedThreshold", False)
        threshold = threshold or self.getData("threshold", list)
        scorer.setThresholds(threshold)

        manipulationAfterPredict = self.getConfig("manipulationAfterPredict", False)
        da = DataManipulation.getInstance(manipulationAfterPredict, "test", self.project.config, threshold=threshold)
        batchSize = self.getConfig("eval.batchSize")

        for data in tqdm(testData):
            x, truth = data

            prediction = model.predict(x, returnNumpy=False)
            prediction, truth = da((prediction, truth))

            scorer.score(truth, prediction, trace=True)

        result = scorer.scoreAllRecords()

        return scorer.recordResult, result

    def getExample(self, eventstream):
        diff = np.diff(eventstream.astype(int), prepend=0, append=0)
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0] - 1
        index = random.randint(0, len(starts) - 1)
        return starts[index], ends[index]+1


    def getExamples(self, labelIndex, truth, predictions):
        # labelNames =
        labelName = self.getConfig("classification.labelNames")[labelIndex]
        classNames = self.getConfig("classification.classNames")[labelIndex]

        examples = {}
        truth, predictions = truth.reshape(-1), predictions.reshape(-1)

        for i, name in enumerate(classNames):
            for j, name in enumerate(classNames):
                exampleName = f"{labelName}-{i}-{j}"
                examples[exampleName] = []
                eventStream = (truth == i) & (predictions == j)
                if any(eventStream):
                    for e in range(self.exampleCount):
                        # example = self.getExample(occurrences, occurrencesOthers, len(truth))
                        example = self.getExample(eventStream)
                        examples[exampleName].append(example)

        return examples

    def eventEvaluation(self):
        # recordResults, segmentResults = self.getData("evalResults", list)
        testData, recordsMap = self.getTestDataAndRecordMap()

        with self.project:
            self.project.config.update(self.getConfig("eventEval", {}))

            evalMetrics = self.getConfig("eval.metrics")
            classNums = self.getConfig("numClasses", [2])
            labelNames = self.getConfig("classification.labelNames")
            predictionNames = self.getConfig("classification.predictionSignals")
            predictionFrequencies = self.getConfig("classification.predictionFrequencies")
            ignoreIndex = self.getConfig("classification.ignoreIndex", -1)
            scorerTypes = [(EventScorer if sc == "event" else Scorer) for sc in self.getConfig("classification.scorerTypes")]

            threshold = self.getConfig("fixedThreshold", False)
            thresholds = threshold or self.getData("threshold", list)
            mScorer = MultiScorer(classNums, evalMetrics, scorerNames=labelNames, ignoreClasses=[ignoreIndex], scorerClasses=scorerTypes)
            for threshold, s in zip(thresholds, mScorer.scorer.values()):
                s.majorityVote = self.getConfig("eventEval.tpStrat", "overlap") == "majority"
                s.noTN = self.getConfig("eventEval.tnStrat", "eventcount") == "noTN"
                s.threshold = threshold

            manipulationAfterPredict = self.getConfig("manipulationAfterPredict", False)
            da = DataManipulation.getInstance(manipulationAfterPredict, "test", self.project.config, threshold=thresholds)

            metaData = pd.DataFrame(self.getTestMetadata())
            metaData.replace("M", None, inplace=True)
            # metaData["indexArousal"] = metaData["indexArousal"].astype(float)
            numClasses = self.getConfig("numClasses")

            model = self.getModel()
            
            resultRows = []
            result = {}
            # for recordIndex in tqdm(range(recordCount)):
            for recordIndex, data in tqdm(enumerate(testData), total=len(testData)):
                x, truth = data

                recordId = recordsMap[recordIndex]
                resultRow = {"recordId": recordId}

                sleepDataTruth = SleepMetaData()
                sleepDataPredicted = SleepMetaData()

                if len(x.shape) == 2:
                    x = x.reshape([1] + list(x.shape))
                    truth = truth.reshape([1] + list(truth.shape))

                prediction = model.predict(x, returnNumpy=False)
                prediction, truth = da((prediction, truth))

                # for labelIndex, labelName in enumerate(recordResults.keys()):
                for labelIndex, labelName in enumerate(labelNames):
                    predictionName = predictionNames[labelIndex]
                    predictionFrequency = predictionFrequencies[labelIndex]

                    # recordResult = recordResults[labelName][recordIndex]
                    numClass = numClasses[labelIndex]

                    scorer = mScorer.scorer[labelName]
                    labelPrediction = prediction[labelIndex] if isinstance(prediction, list) else prediction[:, :, labelIndex]
                    labelTruth = truth[labelIndex] if isinstance(truth, list) else truth[:, :, labelIndex]

                    predictionSignal = labelPrediction.reshape(-1)
                    labelTruth = labelTruth.reshape(-1)

                    # score the prediction
                    r = scorer.score(labelTruth, labelPrediction)
                    # r = scorer.score(labelTruth.reshape(-1), labelPrediction.reshape(-1, numClass))
                    resultRow.update({f"{m}_{labelName}": v for m,v in r.items()})

                    # add examples
                    # resultRow[f"examples_{labelName}"] = self.getExamples(labelIndex, labelTruth, labelPrediction)


                    recordData = metaData.query(f'recordId == "{recordId}"')
                    recordData = recordData.iloc[0] if len(recordData) == 1 else {}
                    sleepDataTruth.addSignal(predictionName, labelTruth, frequency=predictionFrequency)
                    sleepDataPredicted.addSignal(predictionName, scorer.flattenPrediction(predictionSignal), frequency=predictionFrequency)

                for metricName in sleepDataPredicted.metaDataMap.keys():
                    resultRow[f"{metricName}-software"] = (
                        recordData[metricName].item()
                        if metricName in recordData and bool(recordData[metricName].tolist())
                        else 0
                    )
                    resultRow[f"{metricName}-truth"] = sleepDataTruth.getMetaData(metricName)
                    resultRow[f"{metricName}-prediction"] = sleepDataPredicted.getMetaData(metricName)

                resultRows.append(resultRow)
            
            for name, scorer in mScorer.scorer.items():
                allLabelResults = scorer.scoreAllRecords()
                result.update({f"{m}_{name}": v for m,v in allLabelResults.items()})
        
        return resultRows, result

    def generateData(self, name):
        if name == "evalResults":
            segmentResults = self.segmentEvaluation(name)
            self.registerData("evalResults", segmentResults)
        elif name == "eventResults":
            eventResults = self.eventEvaluation()
            self.registerData("eventResults", eventResults)

    def main(self):
        segmentResultsRecords, segmentResults = self.getData("evalResults")

        self.logSuccess(f"result segments: {segmentResults}")