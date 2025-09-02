from pathlib import Path
from pyPhases import Phase

from pyPhasesML import ModelManager
from pyPhasesRecordloader import RecordLoader, ChannelsNotPresent

class VisualizeConfig(Phase):

    def main(self):
        config = self.project.config
        verbosity = 1

        self.log("Pipeline Summary")
        self.log("===========================================")

        recordLoader = RecordLoader.get()
        # Data loading
        self.log("\n############## Data Loading ##############")
        self.log(f"Database: {config['dataBase']}")
        # self.log(f"   Database Version: {config['dataBaseVersion']}")

        self.log(f"Loader: {config['useLoader']}")
        recordLoaderClass = type(recordLoader).__name__
        self.log(f"RecordLoader: {recordLoaderClass}")
        self.log(f"Dataset Path: {config['filePath']} - exists: {Path(config['filePath']).exists()}")

        # Record filtering
        # self.log("")
        self.log("\n############## Record Filtering ##############")
        dataversion = config["dataversion"]

        if "recordIds" in dataversion and dataversion["recordIds"] is not None:
            self.log(f"Specific Record IDs: {dataversion['recordIds']}")
            self.log(f"Record Count: {len(dataversion['recordIds'])}")
        else:
           self.log(f"Datasplit:")
           self.log(dataversion)
           self.log(f"{dataversion['split']}")
           recordIds = self.getData("allDBRecordIds", generate=False)
           self.log(f"   RecordCount: {len(recordIds)}")

        # # Data preprocessing
        # self.log("\n3. Data Preprocessing:")
        # self.log(f"   Input Shape: {config['inputShape']}")
        # self.log("   Segment Manipulations:")
        # for manipulation in config['segmentManipulation']:
        #     self.log(f"   - {manipulation['name']}")

        # Channel preprocessing
        # self.log("")
        self.log("\n############## Channel Preprocessing ################")
        
        if verbosity < 2:
            self.log(f"Available channels in the dataset: {recordLoader.targetSignals}")

        self.log("Channels:")
        preprocessingConfig = config['preprocessing']
        usedTypes = []
        self.log(f"Target channel samplingrate: {preprocessingConfig['targetFrequency']}")
        
        for index, channels in enumerate(preprocessingConfig['targetChannels']):
            channelFound = False
            for channelName in channels:
                try:
                    channelType = recordLoader.getSignalTypeByName(channelName)
                    self.log(f"Channel {index+1}: (one of {channels}): {channelName} - Type: {channelType}")
                    channelFound = True
                    usedTypes.append(channelType)
                    break # only the first channel will be processed
                except ChannelsNotPresent:
                    continue

            if not channelFound:
                self.logError(f"Channel {index+1}: No channels found for {channels} Available Channels in the dataset: {recordLoader.targetSignals}")

                
            # self.log("")
            # self.log(f"   - {channel['name']} (Type: {channel['type']})")
        # self.log("")
        self.log("\n############## Labels ##############")
        self.log(f"Target label samplingrate: {preprocessingConfig['labelFrequency']}")
        self.log(f"Label Channels: {config['labelChannels']}")
        self.log(f"Event Manipulation: {preprocessingConfig['extendEvents']}")


        # self.log("")
        self.log("\n############## Preprocessing Steps ##############")
        for channelType in usedTypes:
            steps = config['preprocessing']['stepsPerType'][channelType]
            stepsStr = ""
            if isinstance(steps, list):
                stepsStr = [step['name'] for step in steps]
            else: # is dict
                stepsStr = [step['name'] for step in steps.values()]
            self.log(f"Channel-Type {channelType}: {stepsStr}")

        
        # self.log("")
        self.log("\n############## Data Manipulation ##############")
        inputType = "record wise" if config["recordWise"] else "segment wise"
        self.log(f"Manipulation Input: {inputType}")
        if not config["recordWise"]:
            self.log(f"   Segment Size Channel: {config['segmentLength']}")
            self.log(f"   Segment Size Label: {config['segmentLengthLabel']}")
        
        stepsTraining = [s["name"] for s in config["segmentManipulation"]]
        stepsValidation = [s["name"] for s in config["segmentManipulationEval"]]

        stepsBatch = [s["name"] for s in config["batchManipulation"]]

        self.log(f"Steps (Training): {stepsTraining}")
        self.log(f"Steps (Validation/Test): {stepsValidation}")
        self.log(f"Steps (Batch): {stepsBatch}")
        # Model
        # self.log("")
        self.log("\n############## Model ##############")
        self.log(f"Model Name: {config['modelName']}")
        self.log(f"Input Shape: {config['inputShape']}")

        # self.log("")
        self.log("\n############## Training ##############")
        trainingParameter = self.getConfig("trainingParameter")

        model = ModelManager().getModel()
        lossFunction = model.getLossFunction()
        lossFunction = lossFunction if isinstance(lossFunction, str) else type(lossFunction).__name__

        self.log(f"Batch Size: {trainingParameter['batchSize']}")
        self.log(f"Learningrate: {trainingParameter['learningRate']}")
        self.log(f"Learningrate Decay: {trainingParameter['learningRateDecay']}")
        self.log(f"Cyclic Learningrate: {trainingParameter['cyclicLearningRate']}")

        self.log(f"Loss Function: {lossFunction}")
        self.log(f"Optimizer: {trainingParameter['optimizer']}")
        self.log(f"Early Stopping: {trainingParameter['stopAfterNotImproving']}")
        self.log(f"Max Epochs: {trainingParameter['maxEpochs']}")
        # model = ModelManager().getModel()
        # torchModel = model.model
        # outputShape = torchModel.output_shape

        self.log("\n############## Output ##############")
        self.log(f"Number of Labels: {config['numLabels']}")
        self.log(f"Labels: {config['classification']['labelNames']}")
        self.log(f"Classes: {config['classification']['classNames']}")

        self.log("\n############## Postprocessing ##############")
        postSteps =  [s["name"] for s in config["manipulationAfterPredict"]]
        self.log(f"Postprocessing Steps: {postSteps}")
        thresholdsStr = f"fixed: {config['fixedThresholds']}" if "fixedThresholds" in config else f"will be optimized, using {config['thresholdMetric']} on {config['optimizeOn']}" 
        self.log(f"Thresholds: {thresholdsStr}")
        # self.log("   Model Architecture:")
        # pself.log.pself.log(config['model'], indent=4)

        # # Output
        # self.log("\n6. Output:")
        # self.log(f"   Number of Classes: {config['numClasses']}")
        # self.log(f"   Classification: {config['classification']['name']}")
        # self.log("   Class Names:")
        # for class_name in config['classification']['classNames']:
        #     self.log(f"   - {class_name}")