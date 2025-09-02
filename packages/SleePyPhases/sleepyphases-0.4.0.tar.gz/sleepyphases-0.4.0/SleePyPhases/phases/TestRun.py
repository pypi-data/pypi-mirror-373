from pathlib import Path


from SleePyPhases import SignalPreprocessing as SP, PreManipulation as PM, FeatureExtraction as FE, DataManipulation as DM
from SleePyPhases.phases.Extract import Extract
from SleePyPhases.phases.BuildDataset import BuildDataset
from pyPhases import Phase
from pyPhasesRecordloader import RecordLoader
import os
from pyPhasesML import ModelManager, TrainingSetLoader

class TestRun(Phase):
    useMultiThreading = False
    def main(self):
        import numpy as np
        import pandas as pd
        
        debugConfig = self.getConfig("debugConfig", {})
        print(f"Overwrite Config with debug values in debugConfig: {debugConfig}")

        with self.project:
            self.project.updateConfig(debugConfig)
            loader = self.getConfig("useLoader")
            rl = RecordLoader.get()
            # rl.debug = True

            if not self.useMultiThreading:
                self.log("Disable multi threading for better error messages. To test multi threading, set TestRun.useMultiThreading to True")
                Extract.useMultiThreading = False
                BuildDataset.useMultiThreading = False
            
            self.log("Testing pyPhases settings")
            dataPath = Path(self.getConfig("data-path"))
            if dataPath.exists():
                self.logSuccess(f"Path {dataPath} exists: {dataPath.exists()}")
                
                # Test if directory is writable
                if os.access(dataPath, os.W_OK):
                    self.logSuccess(f"Data Path ({dataPath}) is writable")
                else:
                    self.logError(f"Data Path ({dataPath}) is not writable. Make sure to set the correct path (Config: data-path) and permissions.")
                    exit(1)
            else:
                self.logError(f"Data Path ({dataPath}) does not exist. Please set the correct path (Config: data-path)")
                exit(1)

            testRunData = dataPath / "testrun"
            self.log(f"Creating a new Data Folder ({testRunData.as_posix()}) for the testrun")
            if not testRunData.exists():
                testRunData.mkdir()
            self.setConfig("data-path", testRunData)
            self.project.prepareAllPhases()
            # else:
            #     # remove all files from the testrun folder
            #     for f in testRunData.iterdir():
            #         f.unlink()

            self.log("Creating a new Data Folder for the testrun")

            self.log(f"Test specified RecordLoader: {loader} ({type(rl)})")
            datasetPath = Path(rl.filePath)
            if datasetPath.exists():
                self.logSuccess(f"RL Path ({rl.filePath}) exists: {Path(rl.filePath).exists()}")
            else:
                self.logError(f"RL Path ({rl.filePath}) does not exist. Make sure to download the dataset and set the correct path (Config: {loader}-path)")
                exit(1)

            self.setConfig("testrun", True)

            self.log("Test generating dataset metadata, for first records")
            df = self.getData("metadata", pd.DataFrame)
            self.log(f"Metadata: {df.head()} / {df.shape}")

            if len(df) > 0:
                self.logSuccess("Dataset records loaded")
            else:
                self.logError("Dataset records not loaded")
            # metadata-channels, dataIsFinal

            self.log("Test data version and split")
            dm = self.getData("dataversionmanager")
            self.log(f"Splits (assuming all records exist): {dm.splits}")

            self.log("For debugging purpose, we will reduce the split using the same 2 records for all splits")
            dm.splits["training"][0] = slice(0, 2)
            dm.splits["validation"][0] = slice(0, 2)
            dm.splits["test"][0] = slice(0, 2)

            self.log("Test extracting data with preprocessing defined in (Config: preprocessing)")
            self.log(f"Preprocessing Config: {self.getConfig('preprocessing')}")
            self.log(f"Preprocessing target frequency: {self.getConfig('preprocessing.targetFrequency')}")
            self.log(f"Preprocessing target labelFrequency: {self.getConfig('preprocessing.labelFrequency')}")
            self.log(f"Preprocessing target channels: {self.getConfig('preprocessing.targetChannels')}")
            # check that resample is in each target signal related preprocessing

            self.log(f"Current SignalPreprocessing Class: {type(SP.getInstance(self.getConfig('preprocessing')))}")
            self.log(f"Current PreManipulation Class: {type(PM.getInstance(self.getConfig('preprocessing')))}")
            # self.log(f"Current FeatureExtraction: {type(FE.getInstance(self.getConfig('preprocessing')))}")
            self.log(f"Current SignalPreprocessing: {self.getConfig('preprocessing.stepsPerType')}")
            self.log(f"Current PreManipulation: {self.getConfig('preprocessing.manipulationSteps')}")
            # self.log(f"Current FeatureExtraction: {type(FE.getInstance(self.getConfig('preprocessing')))}")

            memmapOptions = {
                "dtype": self.getConfig("preprocessing.dtype", "float32"),
            }
            dataExporterSignals = self.getData("data-processed", np.memmap, options=memmapOptions)
            dataExporterFeatures = self.getData("data-features", np.memmap, options=memmapOptions)

            self.logSuccess(f"Extract finished: len X: {len(dataExporterSignals)} / len Y: {len(dataExporterFeatures)}")

            self.log("Test data manipulation")
            manipulationSteps = self.getConfig("segmentManipulation")
            self.log(f"Current segmentManipulation: {manipulationSteps}")
            segmentManipulation = DM.getInstance(manipulationSteps, "training", self.project.config)
            self.log(f"Current DataManipulation Class: {type(segmentManipulation)}")
            # segmentManipulation = DM.getInstance(manipulationSteps, "training", self.project.config, recordMetadata=recordMetaData)
            
            X, Y = dataExporterSignals[0], dataExporterFeatures[0]
            X, Y = segmentManipulation((X, Y), None, 0)

            self.logSuccess(f"Segment Manipulation finished: X: {X.shape} / Y: {Y.shape}")

            self.log(f"Test Model: {self.getConfig('modelName')}")

            model = ModelManager.getModel()
            model.config.logPath = testRunData / "logs"

            self.log(f"Current Model: {type(model)}")
            self.log(model.summary())
            train = self.project.generateData("dataset-training")
            val = self.project.generateData("dataset-validation")
            trainingsSet = TrainingSetLoader(trainingData=train, validationData=val)
            model.debug = True
            trainedModel = model.train(trainingsSet)

            self.logSuccess("Debug Model trained")




            # allDBRecordIds
            # self.getData("allRecordIds")
            # extract data
            # build data
            # data manipulation
            # load model
            # training
            # validation
            # threshold optimization
            # segment evaluation
            # event evaluation