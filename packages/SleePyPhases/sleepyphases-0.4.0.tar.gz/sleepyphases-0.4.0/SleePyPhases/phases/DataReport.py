from pathlib import Path

import numpy as np
from SleePyPhases.PSGEventManager import PSGEventManager
from pyPhases import Phase
from pyPhasesRecordloader import RecordLoader, RecordSignal, Signal


from SleePyPhases.SignalPreprocessing import SignalPreprocessing
from SleePyPhases.phases.Extract import RecordProcessor
import pandas as pd


class DataReport(Phase):
    exampleCount = 5
    exampleSeed = 5
    examplePaddingInS = 2
    exampleSecondsPerInch = 2
    highlight = None
    exampleSkipClass = []
    exampleRawMaxSamplingRate = 256

    def createReportFolder(self, path):
        if not Path(path).exists():
            Path(path).mkdir(parents=True, exist_ok=True)

    def plotRecordSignal(self, classExamples, recordSignal: RecordSignal, fileName, sliceValues=None, highlights=None):
        labelNames = self.getConfig("classification.labelNames")
        classificationName = self.getConfig("classification.name")
        labelFrequency = self.getConfig("preprocessing.labelFrequency")
        samplingrate = recordSignal.targetFrequency
        split = self.getConfig("datasetSplit")

        for classIndex, sliceValues in classExamples.items():
            className = labelNames[classIndex]
            if classIndex in self.exampleSkipClass or className in self.exampleSkipClass:
                continue
            paddingInS = self.examplePaddingInS
            padding = paddingInS * samplingrate
            highlights = []

            factor = samplingrate / labelFrequency
            sliceValues = int(sliceValues[0] * factor), int(sliceValues[1] * factor)

            if self.highlight is not None:
                s, e = self.highlight
                s += paddingInS
                e = e + paddingInS if e > 0 else e - paddingInS
                highlights.append((s, e))

            self.plot.plotRecordSignal(
                recordSignal,
                sliceValues,
                resample=False,
                padding=padding,
                secondsPerInch=self.exampleSecondsPerInch,
                highlights=highlights,
                title="Example for %s/%s in record '{record}' from {from}" % (classificationName, className),
            )
            self.plot.save(f"{fileName}-{split}-{className}")

    def plotExamples(self, stats: dict, name=""):
        currentSplit = self.getConfig("datasetSplit")
        channelNames = [c[0] for c in self.getConfig("preprocessing.targetChannels")]
        classificationName = self.getConfig("classification.name")

        recordStats = stats["records"]
        exampleCount = min(self.exampleCount, len(recordStats))
        # pick random records
        randomRecordIndexes = np.random.choice(len(recordStats), exampleCount, replace=False)

        dm = self.getData("dataversionmanager")
        recordIds = dm.getRecordsForSplit(currentSplit)

        memmapOptions = {
            "dtype": self.getConfig("preprocessing.dtype"),
        }
        dataExporterSignals = self.project.getData("data-processed", np.memmap, options=memmapOptions)
        dataExporterFeatures = self.project.getData("data-features", np.memmap, options=memmapOptions)
        # class example are in the preprocessed label channel resolution
        labelFrequency = self.getConfig("preprocessing.labelFrequency")

        for i, recordIndex in enumerate(randomRecordIndexes):
            # create recordsignal for processed data
            samplingrate = self.getConfig("preprocessing.targetFrequency")
            X, Y = dataExporterSignals[recordIndex], dataExporterFeatures[recordIndex]
            classExamples = recordStats[recordIndex]["classExamples"]
            recordSignal = RecordSignal.fromArray(
                X, sourceFrequency=samplingrate, targetFrequency=samplingrate, names=channelNames, transpose=True
            )
            preprocessing = SignalPreprocessing(self.project.config["preprocessing"])
            labelSignal = Signal(classificationName, Y[:, 0], labelFrequency)
            preprocessing.resample(labelSignal, recordSignal, targetFrequency=samplingrate)
            recordSignal.addSignal(labelSignal)
            recordSignal.recordId = recordIds[recordIndex]

            self.plotRecordSignal(classExamples, recordSignal, f"example-{i}-processed")

            # create recordsignal for raw data
            recordId = recordIds[recordIndex]
            recordLoader = RecordLoader.get()
            recordSignal, events = recordLoader.loadRecord(recordId)
            useSPT = self.getConfig("preprocessing.cutFirstAndLastWake")
            events = RecordProcessor.tailorToSleepScoring(recordSignal, events, useSPT=useSPT)

            samplingrate = int(max(s.frequency for s in recordSignal.signals))
            samplingrate = min(samplingrate, self.exampleRawMaxSamplingRate)
            recordSignal.targetFrequency = samplingrate

            for s in recordSignal.signals:
                if s.frequency != samplingrate:
                    self.logWarning("Resampled signal %s from %i to %i" % (s.name, s.frequency, samplingrate))
                    preprocessing.resample(s, recordSignal, targetFrequency=samplingrate)

            # create and and add label signal
            em = PSGEventManager()
            signalLength = recordSignal.getShape()[1]
            eventSignals = em.getEventSignalFromList(
                events,
                signalLength,
                targetFrequency=samplingrate,
                forceGapBetweenEvents=False,
            )
            labelSignal = Signal(classificationName, eventSignals[classificationName], samplingrate)
            recordSignal.addSignal(labelSignal)

            self.plotRecordSignal(classExamples, recordSignal, f"example-{i}-raw")

    def plotClassDistributions(self, df):
        checkMetaColumns = ["psg_type", "rls_plmd", "insomie", "hypersomnie", "rbd", "sbas_nachrdi_lt5_lt15"]
        for col in checkMetaColumns:
            if col in df.columns:
                self.plot.plotClassDistribution(df.groupby(col)["recordId"].count())
                self.plot.save(name=f"distribution_{col}")

    def main(self):
        from SleePyPhases.Plot import Plot
        
        modelConfigString = self.project.getDataFromName("dataset-bySplit").getTagString()
        self.reportFolder = self.getConfig("reportfolder") + "/" + modelConfigString
        self.createReportFolder(self.reportFolder)
        self.setConfig("datasetSplit", "test")

        analyseDatasets = self.getConfig("datasetSplits")
        self.plot = Plot(self.reportFolder)
        np.random.seed(self.exampleSeed)

        dm = self.getData("dataversionmanager")
        df = pd.DataFrame(self.getData("metadata", list))

        df = df.fillna(
            {
                "rls_plmd": "None",
                "hypersomnie": "None",
                "insomie": "None",
                "rbd": "None",
                "sbas_nachrdi_lt5_lt15": "None",
                "diagnose_rdi_lt5_lt15_nurdiag": "None",
            }
        )

        for datasetName in analyseDatasets:
            self.setConfig("datasetSplit", datasetName)
            stats = self.getData("datasetstats", dict)
            labelNames = stats["labels"]
            classCountDict = dict(zip(labelNames, stats["classCounts"]))

            self.plot.plotClassDistribution(classCountDict, title=f"{datasetName} - Claas Distribution")
            self.plot.save(name=f"{datasetName}-classCounts")

            # plot classification examples
            self.plotExamples(stats)

            # plot metadata distribution
            records = dm.getRecordsForSplit(datasetName)
            self.plotClassDistributions(df.query("recordId in %s" % records))

        self.plotClassDistributions(df)

        testIds = dm.getRecordsForSplit("test")
        testRecords = df.query("recordId in %s" % testIds)

        recordIdsAll = dm.getRecordsForSplit("test") + dm.getRecordsForSplit("trainval")
        allRecords = df.query("recordId in %s" % recordIdsAll)

        stats = ["gender"]

        for r in [allRecords, testRecords]:
            if "gender" in r.columns:
                stats = {
                    "femalePercentage": len(r.query("gender == 'female'")) / len(r),
                }
                dataPoints = ["age", "indexArousal", "countArousal", "ahi", "tst"]
                for d in dataPoints:
                    stats[d] = "%f2±%s" % (r[d].mean(), r[d].std())
                    print("%s: %s" % (d, stats[d]))
                print(stats)
