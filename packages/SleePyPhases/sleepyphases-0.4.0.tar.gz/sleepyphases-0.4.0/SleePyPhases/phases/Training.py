import contextlib
from pathlib import Path

import numpy as np
from pyPhases import Phase
from pyPhasesML import Model, ModelManager, TrainingSetLoader
from pyPhasesML.adapter.torch import CyclicLearningrate, FindLearningRate


class Training(Phase):
    def prepareConfig(self):
        shape = self.getConfig("inputShape")  # [segmentLength, channelCount]

        self.log(f"Set the inputshape to {str(shape)}")
        self.setConfig("inputShape", shape)

    def createLogFolder(self, path):
        if not Path(path).exists():
            Path(path).mkdir(parents=True, exist_ok=True)
        # you can throw an error if you want to prevent overwriting you training

    def train(self):
        model = ModelManager.getModel()
        # log everything in a specific folder derived from config values
        modelConfigString = self.project.getDataFromName("modelState").getTagString()
        logPath = f"logs/{modelConfigString}/"
        self.createLogFolder(logPath)
        model.config.logPath = logPath

        # load the trainingsdata from filesystem or generate it
        train = self.project.generateData("dataset-training")
        val = self.project.generateData("dataset-validation")
        trainingsSet = TrainingSetLoader(trainingData=train, validationData=val)

        findLR = self.getConfig("trainingParameter.findCyclicLearningRate", False)
        cyclicLR = self.getConfig("trainingParameter.cyclicLearningRate", False)

        if findLR:
            findinLR = FindLearningRate(model.config, minLR=0.00001, maxLR=2, iterations=3)
            model.registerCB(findinLR)
        elif cyclicLR:
            model.registerCB(CyclicLearningrate(model.config))

        self.log(model.summary())
        self.project.saveConfig(f"{logPath}model.config", "modelState")
        self.project.saveConfig(f"{logPath}project.config")
        trainedModel = model.train(trainingsSet)

        # save the model state and relevant config values
        self.logSuccess(f"Model trained and saved to {logPath}")
        self.logSuccess(f"Model trained {model.validationMetrics[0]}: {model.bestMetric}")

        self.gridOutput = {
            "epochs": model.fullEpochs,
            "best": model.bestMetric,
        }
        return trainedModel

    def generateData(self, name):
        trainedModel = self.train()
        self.project.registerData("modelState", trainedModel)
        self.project.registerData("modelStateConfig", self.project.getDataFromName("modelState").getDependencyDict())

    def main(self):
        startfold = self.getConfig("startFold", 0)
        folds = max(self.getConfig("dataversion.folds", 1), 1)
        endfold = self.getConfig("endFold", folds)
        self.gridOutput = {
            "epochs": 0,
            "best": 0,
        }

        if startfold >= folds:
            self.logError(f"startFold {startfold} is bigger than the number of folds {folds}")
        if endfold <= startfold:
            self.logError(f"endfold {endfold} is smaller than start folds {startfold}")

        gridOutputs = []
        for fold in range(startfold, endfold):
            # save model state (random initialisation or pretrained)
            startState = ModelManager.getModel().model.state_dict()
            self.setConfig("fold", fold)
            # only train if it doesnt allready exist
            self.getData("modelState", Model)
            # unregister current model for the next fold
            with contextlib.suppress(KeyError):
                self.project.unregister("modelState")
                self.project.unregister("modelStateConfig")
            gridOutputs.append(self.gridOutput)
            # reset model state
            ModelManager.getModel().model.load_state_dict(startState)

        self.project.gridOutput = {
            "epochs": str(np.mean([m["epochs"] for m in gridOutputs])),
            "best": str(np.mean([m["best"] for m in gridOutputs])),
            "folds": len(gridOutputs),
        }
