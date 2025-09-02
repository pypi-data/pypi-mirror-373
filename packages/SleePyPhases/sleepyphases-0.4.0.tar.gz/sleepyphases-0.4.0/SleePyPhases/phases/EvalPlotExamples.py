import numpy as np

from pyPhases import Phase
from pyPhasesRecordloader import RecordSignal, Signal

from SleePyPhases.Plot import Plot
from SleePyPhases.DataManipulation import DataManipulation
from datetime import timedelta



class EvalPlotExamples(Phase):
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


    def plotRecordSignal(
        self, recordSignal: RecordSignal, fileName, sliceValues=None, highlights=None, offset=0, title="Example"
    ):
        from matplotlib import pyplot as plt
        samplingrate = recordSignal.targetFrequency
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

        plt.clf()
        plot = Plot(self.evalPath)
        plot.eventMap = {}
        
        labelNames = self.getConfig("classification.labelNames")
        def mergePrediction(signal, axs, index):

            if signal.name in labelNames:
                fig = plt.gcf()
                fig.delaxes(axs[index+1])

                ax = axs[index]
                ax.set_ylim(0, 1.1)
                axs[index] = ax
                axs[index+1] = ax

                current_height = ax.get_position().height

                for i in range(index+2, len(axs)):
                    axs[i].set_position(axs[i].get_position().translated(0, current_height + 0.02))


        plot.on("beforePlotSignal", mergePrediction)

        thresholds = self.threshold
        def addThreshold(signal, axs, index):
            # from matplotlib import pyplot as plt
            if signal.name in labelNames:
                threshold = thresholds[labelNames.index(signal.name)]
                axs[index].axhline(y=threshold, color="red")
                axs[index].text(1, threshold + 0.02, f"{signal.name} Threshold", color="red")

        plot.on("afterPlotSignal", addThreshold)

        fig = plot.plotRecordSignal(
            recordSignal,
            sliceValues,
            resample=False,
            padding=padding,
            secondsPerInch=self.exampleSecondsPerInch,
            highlights=highlights,
            title=title,
        )

        fig.axes[-1].set_xlabel("Time (s)")
        fig.axes[-1].xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: str(timedelta(seconds=val))))

        plot.save(f"examples/{fileName}")


    def plotRecordSignalWithClassExamples(
        self, label, classExamples, recordSignal: RecordSignal, fileName, sliceValues=None, highlights=None, offset=0, classNames=None, threshold=None, labelName=""
    ):

        classificationNames = {}
        for i, name1 in enumerate(classNames):
            for j, name2 in enumerate(classNames):
                classificationNames[f"{i}-{j}"] = f"{name1} as {name2}"

        for classIndex, examples in classExamples.items():
            for eIndex, sliceValues in enumerate(examples):
                className = classificationNames["-".join(classIndex.split("-")[1:])]
                if classIndex in self.exampleSkipClass:
                    continue

                self.plotRecordSignal(
                    recordSignal, 
                    fileName=f"{eIndex}-{fileName}-{label}-{className}", 
                    sliceValues=sliceValues, 
                    highlights=highlights, 
                    offset=offset, 
                    title="Example for %s: %s in record '{record}' from {from}" % (label, className)
                )


    def getRecordSignal(self, recordStats, segmentStats, recordId):
        channelNames = self.getConfig("evalChannelNames")

        exampleCount = 3
        # pick random records
        randomRecordIndexes = np.random.choice(len(recordStats), exampleCount, replace=False)

        testData, dm, recordsMap = self.getExternalTestset()
        recordIds = dm.getRecordsForSplit("test")

        self.setConfig("BuildDataset.useMultiThreading", False)
        da = DataManipulation.getInstance([], "test", self.project.config)

        recordIndex = recordIds.index(recordId)
        samplingrate = self.getConfig("preprocessing.targetFrequency")
        X, Y = testData[recordIndex]

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
        labelOrdered = {i:label for i, label in enumerate(labelNames)}
        
        for labelIndex, label in labelOrdered.items():
            labelSignal = Signal(label, Y[:, labelIndex], samplingrate)

            recordSignal.addSignal(labelSignal)


            prediction = segmentStats[label][recordIndex]["prediction"]
            # add prediction
            offset = (len(Y[:, 0]) - prediction.shape[0]) // 2
            prediction, _ = da._fixeSizeSingleChannel(prediction.reshape(1, -1, 1), 2**21, fillValue=0, position="center")
            predictionSignal = Signal(f"{label} Prediction", prediction.reshape(-1), samplingrate)
            recordSignal.addSignal(predictionSignal)

        return recordSignal

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
            
            labelNames = self.getConfig("classification.classNames")
            mainLabelName = labelName
            mainLabelIndex = labelNames.index(labelName)

            # labelOrdered = {i:label for i, label in enumerate(labelNames) if label != mainLabelName}
            # labelOrdered[mainLabelIndex] = mainLabelName
            labelOrdered = {i:label for i, label in enumerate(labelNames)}
            # labelOrdered[mainLabelIndex] = mainLabelName


            
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
            self.plotRecordSignalWithClassExamples(labelName, classExamples, recordSignal, f"example-{i}-processed", classNames=classNames, offset=offset, threshold=self.threshold[mainLabelIndex], labelName=labelName)

   
    def plotVideoExample(self, recordStats, segmentStats, recordId, start, end):
        
        testData, dm, recordsMap = self.getExternalTestset()
        recordIds = dm.getRecordsForSplit("test")

        recordId = "acq_238127226"
        recordSignal = self.getRecordSignal(recordStats, segmentStats, recordId)

        start = 3*60*60 + 18 + 60 + 34
        start *= 50
        end = start + 5*60*50
        end = 2097152

        start = 648600
        end = start + 5*60*50
        start, end = (618600, 678600)
        # start, end = (510000, 550000)

        export = self.project.getExporterForType(list)
        export.write("myexample", recordSignal)
        recordSignal = export.read("myexample")

        self.plotRecordSignal(
            recordSignal=recordSignal,
            fileName="blub",
            sliceValues=[start,end]
        )
        # self.plotRecordSignal("Sleep", classExamples, recordSignal, f"example-{i}-processed", classNames=classNames, offset=offset, threshold=self.threshold[mainLabelIndex], labelName=labelName)
        pass



    def main(self):
        import pandas as pd
        
        threshold = self.getConfig("fixedThreshold", False)
        self.threshold = threshold or self.getData("threshold", float)

        modelConfigString = self.project.getDataFromName("eventResults").getTagString()
        evalPath = f"eval/{modelConfigString}/"
        self.evalPath = evalPath
        labelNames = self.getConfig("classification.labelNames")
        segmentResultsRecords, segmentResults = self.getData("evalResults", list)
        resultRows, result = self.getData("eventResults", list)

        start = 3*60*60 + 18 + 60 + 34
        start *= 50
        end = start + 5*60*50

        # self.plotVideoExample(resultRows, segmentResultsRecords, "acq_238127226", start, end)
        for label in labelNames:
            self.plotExamples(recordStats=resultRows, segmentStats=segmentResultsRecords, labelName=label)
        self.log(f"Eval finished: {evalPath}")

