from pathlib import Path

from pyPhases import Phase
from pyPhasesML import DataversionManager, Scorer
from pyPhasesRecordloader import RecordLoader



class Setup(Phase):
    def prepareConfig(self):
        numLabels = len(self.getConfig("classification.labelNames", []))
        self.setConfig("numLabels", numLabels)

        numClasses = [len(c) for c in self.getConfig("classification.classNames", [])]
        self.setConfig("numClasses", numClasses)
        
        defaultValidationbatchManipulation = self.getConfig("segmentManipulationEval", self.getConfig("segmentManipulation", []))
        self.setConfig("segmentManipulationEval", defaultValidationbatchManipulation)

        preprocessingConfig = self.getConfig("preprocessing", {})
        if "combineChannels" in preprocessingConfig:
            RecordLoader.get().addCombinedChannels(preprocessingConfig["combineChannels"])


        # default fold is 0 if none is set
        self.setConfig("fold", self.getConfig("fold", 0))
        # self.setConfig("datasetSplits", list(self.getConfig("dataversion.split", {}).keys()))
        self.setConfig("hasFolds", self.getConfig("dataversion.folds", 0) > 0)

        s = Scorer(5)
        s.ignoreClasses = [-1]
        
        def reduceKappa(y_true, y_pred):
            # sleep stages are calculated for 50Hz, reduce to 30s for scoring
            y_pred = y_pred.reshape(-1, 1500, 5)
            y_pred = y_pred.mean(axis=1)
            y_true = y_true[::1500]
            return s.getMetricScorer("kappa")(y_true, y_pred)

        def combineReduceKappa(y_true, y_pred):
            s.reset()
            y_true, y_pred = s.maskedIgnoredValues(y_true, y_pred)
            kappa = reduceKappa(y_true, y_pred)
            print("######SleepStages######")
            print(s.results["confusion"])
            return kappa
        Scorer.registerMetric("reduceAndKappa", reduceKappa, combineReduceKappa)
        
    def getDataVersionManager(self):
        groupedRecords = self.project.getData("allDBRecordIds", list)
        seed = self.getConfig("dataversion.seed", None)
        splits = self.getConfig("dataversion.split", {})
        splits = {} if splits is None else splits


        # check if there are removed records, this can only happen after the extraction
        # dataversionamnager has diffent records before and after extraction!
        with self.project:
            if self.project.dataExistIn("removedRecordIds", list):
                removedRecordIds = self.getData("removedRecordIds", list, generate=False)
                self.log("Removing incomplete records from dataversionmanager")
                groupedRecords = {k: [r for r in v if r not in removedRecordIds] for k, v in groupedRecords.items()}
                # remove empty groups
                groupedRecords = {k: v for k, v in groupedRecords.items() if len(v) > 0}
            else:
                self.logError("no removed records specified! The splits might differ")
        
        # create non manual splits, if not specified
        valSplit = self.getConfig("validationSplit", 0.2)
        testSplit = self.getConfig("testSplit", 0.2)

        dm = DataversionManager(groupedRecords, seed=seed)

        # add manual addes splits
        for splitName in ["training", "validation", "test"]:
            if splitName in splits:
                dm.addSplitBySlices(splitName, splits[splitName])

        # add training folding splits
        if "trainval" in splits:
            foldcount = self.getConfig("dataversion.folds", 0)
            if foldcount > 0:
                dm.addSplitsByFold("training", "validation", splits["trainval"], self.getConfig("dataversion.folds", 0), self.getConfig("fold", 0))
            else:
                dm.addSplitByRemaining("validation", valSplit) # , remainingSplit=trainingSlice
                dm.addSplitByRemaining("training", 1)

            if "training" in splits or "validation" in splits:
                raise Exception("trainval and training/validation split are mutually exclusive. Please remove one of them from the config. This can be caused by loading multiple configs with different splits.")

        if "trainvaltest" in splits:
            foldCount = self.getConfig("dataversion.folds")
            currentFold = self.getConfig("fold", 0)
            testSlice, trainingSlice = dm.getSplitsByPercentage(
                dm.getRemainingSplit(), subLength=1 / foldCount, subPosition=currentFold
            )

            dm.addSplitBySlices("test", testSlice)

            dm.addSplitByRemaining("validation", valSplit) # , remainingSplit=trainingSlice
            dm.addSplitByRemaining("training", 1)

            

        if "test" not in dm.splits:
            dm.addSplitByRemaining("test", testSplit)

        if "validation" not in dm.splits:
            dm.addSplitByRemaining("validation", valSplit)

        if "training" not in dm.splits:
            dm.addSplitByRemaining("training", 1)

        dm.validatDatasetVersion(raiseException=self.getConfig("validatDataset", True))

        return dm
    
    def generateData(self, name):
        if name == "dataversionmanager":
            dm = self.getDataVersionManager()
            self.registerData("dataversionmanager", dm, save=False)
