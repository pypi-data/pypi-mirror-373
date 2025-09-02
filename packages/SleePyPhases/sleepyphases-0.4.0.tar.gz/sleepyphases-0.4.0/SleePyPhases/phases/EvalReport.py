import shutil
from pathlib import Path
from typing import Iterable

import numpy as np

import yaml
from pyPhases import Phase
from pyPhasesRecordloader import RecordSignal, Signal

from SleePyPhases import Plot
from SleePyPhases.DataManipulation import DataManipulation


class EvalReport(Phase):
    allowTraining: bool = True
    exampleSkipClass = ["0-0"]
    examplePaddingInS = 10
    highlight = None
    exampleSecondsPerInch = 2

    def getExternalTestset(self, split="test"):
        with self.project:
            evalConfig = self.getConfig("evalOn")

            # try not to update dataversion, rather replace it completly
            if "dataversion" in evalConfig:
                self.project.config["dataversion"] = {}

            self.project.config.update(evalConfig)
            self.project.trigger("configChanged", None)
            dataset = self.project.getData(f"dataset-{split}", list)
            dm = self.getData("dataversionmanager")
            recordsMap = dm.getRecordsForSplit(split)

        return dataset, dm, recordsMap

    def createLogFolder(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)
        # Path(path).joinpath("/examples").mkdir(parents=True, exist_ok=True)

    def addAsset(self, name, extension="png", bbox_inches="tight", dpi=300):
        import matplotlib.pyplot as plt
        fullName = name + "." + extension
        # assetPath = Reporter.assetPath + "/" + fullName
        fullPath = self.evalPath + fullName
        self.createLogFolder(Path(fullPath).parent)
        plt.savefig(fullPath, bbox_inches=bbox_inches, dpi=dpi)
        plt.close()

    def plotRecordSignal(
        self, label, classExamples, recordSignal: RecordSignal, fileName, sliceValues=None, highlights=None, offset=0, classNames=None, threshold=None, labelName=""
    ):

        classificationNames = {}
        for i, name1 in enumerate(classNames):
            for j, name2 in enumerate(classNames):
                classificationNames[f"{i}-{j}"] = f"{name1} as {name2}"

        # classificationName = self.getConfig("classification.name")
        labelFrequency = self.getConfig("preprocessing.labelFrequency")
        samplingrate = recordSignal.targetFrequency

        for classIndex, examples in classExamples.items():
            for eIndex, sliceValues in enumerate(examples):
                className = classificationNames["-".join(classIndex.split("-")[1:])]
                if classIndex in self.exampleSkipClass:
                    continue
                paddingInS = self.examplePaddingInS
                padding = paddingInS * samplingrate
                highlights = []

                sliceValues = sliceValues[0] + offset, sliceValues[1] + offset

                sliceValues = sliceValues[0], sliceValues[0] + 50 * 100

                if self.highlight is not None:
                    s, e = self.highlight
                    s += paddingInS
                    e = e + paddingInS if e > 0 else e - paddingInS
                    highlights.append((s, e))

                plot = Plot(self.evalPath)
                from matplotlib import pyplot as plt

                def mergePrediction(signal, axs, index):
                    if signal.name in labelNames:
                        axs[index+1] = axs[index]
                
                plot.on("beforePlotSignal", mergePrediction)

                labelNames = self.getConfig("classification.labelNames")
                
                def addThreshold(signal, axs, index):
                    if signal.name in labelNames:
                        axs[index].axhline(y=threshold[0], color="red")
                        axs[index].text(1, threshold[0] + 0.02, "Threshold", color="red")
                
                plot.on("afterPlotSignal", addThreshold)

                plot.plotRecordSignal(
                    recordSignal,
                    sliceValues,
                    resample=False,
                    padding=padding,
                    secondsPerInch=self.exampleSecondsPerInch,
                    highlights=highlights,
                    title="Example for %s: %s in record '{record}' from {from}" % (label, className),
                )
                if threshold is not None:
                    fig, ax = plt.subplots()
                    from matplotlib import pyplot as plt
                    plt.axhline(y=threshold[0], color="red")
                    plt.text(1, threshold[0] + 0.02, "Threshold", color="red")

                plot.plot.save(f"examples/{eIndex}-{fileName}-{label}-{className}")

    def plotExamples(self, recordStats, segmentStats, name="", labelName=""):
        channelNames = self.getConfig("evalChannelNames")

        exampleCount = 3
        # pick random records
        randomRecordIndexes = np.random.choice(len(recordStats), exampleCount, replace=False)

        testData, dm, recordsMap = self.getExternalTestset()
        recordIds = dm.getRecordsForSplit("test")

        self.setConfig("BuildDataset.useMultiThreading", False)
        da = DataManipulation.getInstance([], "test", self.project.config)

        for i, recordIndex in enumerate(randomRecordIndexes):
            # create recordsignal for processed data
            samplingrate = self.getConfig("preprocessing.targetFrequency")
            X, Y = testData[recordIndex]
            classExamples = recordStats[recordIndex][f"examples_{labelName}"]

            if not isinstance(X, np.ndarray):
                X = X.numpy()

            if not isinstance(Y, np.ndarray):
                Y = Y.numpy()
                

            recordSignal = RecordSignal.fromArray(
                X, sourceFrequency=samplingrate, targetFrequency=samplingrate, names=channelNames, transpose=True
            )

            # add labels

            recordSignal.recordId = recordIds[recordIndex]
            
            labelNames = self.getConfig("classification.labelNames")
            mainLabelName = labelName
            mainLabelIndex = labelNames.index(labelName)

            labelOrdered = {i:label for i, label in enumerate(labelNames) if label != mainLabelName}
            labelOrdered[mainLabelIndex] = mainLabelName


            
            for labelIndex, label in labelOrdered.items():
                labelSignal = Signal(label, Y[:, labelIndex], samplingrate)
                # labelSignal = Signal(classificationName, Y[:, 0], samplingrate)
                recordSignal.addSignal(labelSignal)


                prediction = segmentStats[label][recordIndex]["prediction"]
                # add prediction
                offset = (len(Y[:, 0]) - prediction.shape[0]) // 2
                prediction, _ = da._fixeSizeSingleChannel(prediction.reshape(1, -1, 1), 2**21, fillValue=0, position="center")
                predictionSignal = Signal(f"{label} Prediction", prediction.reshape(-1), samplingrate)
                recordSignal.addSignal(predictionSignal)

            classNames = [f"No {labelName}", labelName]
            classExamples = {index: [(c[0]+offset, c[1]+offset) for c in ce] for index, ce in classExamples.items()}
            self.plotRecordSignal(labelName, classExamples, recordSignal, f"example-{i}-processed", classNames=classNames, offset=offset, threshold=self.threshold[mainLabelIndex], labelName=labelName)
        
    def main(self):
        import pandas as pd
        
        threshold = self.getConfig("fixedThreshold", False)
        self.threshold = threshold or self.getData("threshold", float)

        modelConfigString = self.project.getDataFromName("eventResults").getTagString()

        evalPath = self.getConfig("eval-path", "eval/")
        evalPath = f"{evalPath}/{modelConfigString}/"

        self.createLogFolder(evalPath)

        self.evalPath = evalPath

        self.copyRawData()

        # self.log("save report to: %s" % self.reporter.getFilePath())

        segmentResultsRecords, segmentResults = self.getData("evalResults", list)
        df = pd.DataFrame(segmentResultsRecords).transpose()

        # drop generated columns if they exist
        drop_colums = ["truth", "prediction", "all_values", "pos_values", "ign_values", "neg_values"]
        for col in drop_colums:
            if col in df.columns:
                df = df.drop(columns=[col])

        df.to_csv(f"{evalPath}recordResultsSegment.csv", index=False)

        self.logSuccess(f"result segments: {segmentResults}")
        resultRows, result = self.getData("eventResults", list)
        self.logSuccess(f"result events: {result}")
        df = pd.DataFrame(resultRows)

        
        metrics = self.getConfig("trainingParameter.validationMetrics")
        evalMetrics = self.getConfig("eval.metrics")
        labelNames = self.getConfig("classification.labelNames")

        results = {}
        allMetrics = {mA for m in metrics for mA in m} | {mA for m in evalMetrics for mA in m}
        for labelName in labelNames:
            for m in allMetrics:
                metricName = f"{m}_{labelName}"
                if metricName in result:
                    results[f"{metricName}-ev"] = result[metricName]
                if metricName in segmentResults:
                    results[f"{metricName}-seg"] = segmentResults[metricName]

        relMetaData = self.getConfig("eval.clinicalMetrics")
        for m in relMetaData:
            df[f"{m}-prediction-diff"] = df[f"{m}-prediction"] - df[f"{m}-truth"]
            df[f"{m}-prediction-error"] = df[f"{m}-prediction-diff"].abs()

        df.to_csv(f"{evalPath}recordResultsEvents.csv", index=False)

        self.logSuccess(f"Results: {results}")
        results = {k: float(v) for k, v in results.items() if not isinstance(v, Iterable)}
        with open(f"{evalPath}results.yml", "w") as file:
            yaml.dump(results, file)

        self.project.saveConfig(f"{evalPath}project.config")
        self.log(f"Eval finished: {evalPath}")

    def copyRawData(self):
        modelConfigString = self.project.getDataFromName("modelState").getTagString()
        trainingLogPath = f"logs/{modelConfigString}/"
        shutil.copyfile(trainingLogPath + "log.csv", self.evalPath + "training.log")
        shutil.copyfile(trainingLogPath + "project.config", self.evalPath + "project.json")

    def trainingPlot(self, logFile):
        import matplotlib.pyplot as plt
        import pandas as pd

        self.metrics = self.getConfig("trainingParameter.validationMetrics") 
        df = pd.read_csv(logFile)
        plt.plot(df["epoch"], df["loss"], label="Training Loss")
        plt.plot(df["epoch"], df[self.metrics[0]], label=self.metrics[0])
        self.addAsset("trainingsProcess")

    def modelInfo(self):
        model = self.project.getPhase("Eval").getModel()
        sum = model.summary()
        print(sum)