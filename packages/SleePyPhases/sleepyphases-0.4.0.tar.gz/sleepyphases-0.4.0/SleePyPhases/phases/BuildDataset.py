import numpy as np
from pyPhases import Phase
from pyPhasesML.datapipes import Manipulator, DatasetXY
from pyPhasesML import DataversionManager, DataLoader, RecordMap, MultiSourceMap
from pyPhasesML.exporter.MemmapRecordSegmentsExporter import MemmapRecordSegmentsExporter

from SleePyPhases.DataManipulation import DataManipulation


class BuildDataset(Phase):
    """
    in this phase the raw data is loaded, manipulated and converted into a dataset that can be used for training
    """

    def buildDataRecords(self):
        splitName = self.getConfig("datasetSplit")

        datasetVersions = self.getConfig("datafold.datasets", {"config": {}})
        datasetVersions = datasetVersions if isinstance(datasetVersions, list) else [datasetVersions]

        seed = self.getConfig("datafold.seed", 2024)
        multiSrcMap = MultiSourceMap(seed=None)
        recordMetadata = []
        for sourceVersion in datasetVersions:
            overwriteConfig = sourceVersion["config"]

            with self.project:
                if "dataversion" in overwriteConfig:
                    self.project.setConfig("dataversion", {})

                self.project.updateConfig(overwriteConfig)
                memmapOptions = {
                    "dtype": self.getConfig("preprocessing.dtype", "float32"),
                }
                dataExporterSignals = self.project.getData("data-processed", np.memmap, options=memmapOptions)
                dataExporterFeatures = self.project.getData("data-features", np.memmap, options=memmapOptions)

                dm = self.getData("dataversionmanager", DataversionManager)
                metadata = self.project.getData("metadata", list)
                metadataMap = {r["recordId"]: r for r in metadata.iloc}
                allRecordIds = [r for subgroup in dm.unShuffledgroupedRecords.values() for r in subgroup]

                recordIds = dm.getRecordsForSplit(splitName)
                recordIndexes = [allRecordIds.index(r) for r in recordIds]
                recordMetadata =  recordMetadata + [metadataMap[r] for r in recordIds]  

                # handle segment wise data
                recordLengthsInSegments = None
                if not self.getConfig("recordWise"):
                    segmentLength = self.getConfig("segmentLength")
                    segmentLengthLabel = self.getConfig("segmentLengthLabel", segmentLength)
                    paddedSegments = self.getConfig("segmentPadding", [0, 0])
                    recordLengths = dataExporterSignals.recordLengths

                    dataExporterSignals = MemmapRecordSegmentsExporter(dataExporterSignals, segmentLength, paddedSegments)
                    dataExporterFeatures = MemmapRecordSegmentsExporter(dataExporterFeatures, segmentLengthLabel, paddedSegments)
                  
                    recordLengthsInSegments =[length//segmentLength - sum(paddedSegments) for length in recordLengths]
                    assert all(np.array(recordLengthsInSegments) > 0), "segmentLength (including segmentPadding) is too large for some recordings"

                dataset = DatasetXY(dataExporterSignals, dataExporterFeatures)
                recordSet = RecordMap(dataset, recordIndexes, mappingLengths=recordLengthsInSegments)
                
                multiSrcMap.addRecordMap(recordSet)

        # shuffle recordings or segments
        if self.getConfig("datafold.shuffle", False):
            multiSrcMap.shuffle()
            # use same seed to shuffle the metadata
            np.random.seed(seed)
            np.random.shuffle(recordMetadata)

        return multiSrcMap, recordMetadata
                    

    def buildDatasetManipulatorBySplit(self):
        split = self.getConfig("datasetSplit")

        dataRecords, recordMetaData = self.buildDataRecords()

        useConfigName = "segmentManipulationEval" if split != "training" else "segmentManipulation"
        manipulationSteps = self.getConfig(useConfigName)
        segmentManipulation = DataManipulation.getInstance(manipulationSteps, split, self.project.config, recordMetadata=recordMetaData)
        return Manipulator(dataRecords, segmentManipulation)

    def buildDatasetBySplit(self):
        split = self.getConfig("datasetSplit")
        batchSize = self.getConfig("trainingParameter.batchSize") if split != "test" else self.getConfig("eval.batchSize")
        buildConfig = self.getConfig("BuildDataset", {"useMultiThreading": True})

        manipulator = self.buildDatasetManipulatorBySplit()

        dataloader = DataLoader.build(
            manipulator,
            preload=buildConfig["useMultiThreading"],
            batchSize=batchSize,
            shuffle=self.getConfig("trainingParameter.shuffle", False),
            shuffleSeed=self.getConfig("trainingParameter.shuffleSeed", 2),
        )
        
        manipulationSteps = self.getConfig("batchManipulation")
        segmentManipulation = DataManipulation.getInstance(manipulationSteps, split, self.project.config)
        batchManipulation = Manipulator(dataloader, segmentManipulation)
        
        return batchManipulation

    def generateData(self, name):
        splitName = name[8:]
        if splitName != "":
            self.setConfig("datasetSplit", splitName)

        # dont register the data
        return self.buildDatasetBySplit()

    def main(self):
        self.logError("No dataset is build on default. Please use Extract the data for the dataset or Training to train a model.")
