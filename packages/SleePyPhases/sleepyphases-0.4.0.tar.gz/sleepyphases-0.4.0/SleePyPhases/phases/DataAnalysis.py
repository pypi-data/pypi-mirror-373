import numpy as np
from pyPhases import Phase


class DataAnalysis(Phase):
    """analyse data based on the preprocessed data, and data splits"""

    useMultiThreading = True

    def analyseLabelChannel(self, labelchannel):
        classCount = len(self.stats["classes"])
        segmentClasses = np.zeros(classCount, dtype=np.int32)

        classCount = np.unique(labelchannel, return_counts=True)
        examples = {}
        for i, count in zip(*classCount):
            segmentClasses[int(i)] = count

            # i = 2
            # where the class occurs
            occurrences = np.where(labelchannel == i)[0]
            # remove ascending numbers (only starting points left)
            diff = np.diff(occurrences)
            mask = np.hstack(([True], diff > 1))
            occurrences = occurrences[mask]

            # random starting point
            start = np.random.choice(occurrences)
            # find endpoint
            occurrencesOthers = np.where(labelchannel != i)[0]
            end = occurrencesOthers[occurrencesOthers > start]
            end = end[0] if len(end) > 0 else len(labelchannel)

            start = max(start, 0)
            end = min(end, len(labelchannel))
            examples[int(i)] = (start, end)

        return {
            "segmentClasses": segmentClasses,
            "classExamples": examples,
        }

    def analyseDataset(self, datasetName):
        classCount = len(self.stats["classes"])
        self.stats["classCounts"] = np.zeros(classCount)

        # analyse labels
        data = self.getData(
            "data-features",
            np.memmap,
            options={
                "dtype": self.getConfig("preprocessing.dtype"),
            },
        )

        recordsStats = []
        for record in data:
            # only get stats for last label channel (if ther multiple)
            recordStat = self.analyseLabelChannel(record[:, -1])
            self.stats["classCounts"] += recordStat["segmentClasses"]

            recordsStats.append(recordStat)

        self.stats["records"] = recordsStats

    def generateData(self, name):
        datasetName = self.getConfig("datasetSplit")
        labelNames = self.getConfig("classification.labelNames")
        self.stats = {"labels": labelNames}

        self.analyseDataset(datasetName)
        self.registerData("datasetstats", self.stats)
        self.logSuccess("Stats: %s" % self.stats)

    def main(self):
        analyseDatasets = self.getConfig("datasetSplits")

        for datasetName in analyseDatasets:
            self.setConfig("datasetSplit", datasetName)
            self.generateData("datasetstats")
