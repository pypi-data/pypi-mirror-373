from pyPhases import Phase
from pyPhasesML import Model, ModelManager, Scorer
from tqdm import tqdm

class Validation(Phase):
    allowTraining = False

    def getModel(self) -> Model:
        modelState = self.project.getData("modelState", Model, generate=self.allowTraining)
        model = ModelManager.getModel(True)
        model.build()
        model.loadState(modelState)
        return model

    def main(self):
        scorer = Scorer(classNames=self.getConfig("classification.labelNames"), trace=True)
        scorer.metrics = self.getConfig("trainingParameter.validationMetrics")
        scorer.ignoreClasses = [self.getConfig("ignoreClassIndex")]

        model = self.getModel()
        validationData = self.project.generateData("dataset-validation")

        for x, t in tqdm(validationData):
            p = model.predict(x, get_likelihood=True, returnNumpy=True)
            scorer.score(t, p, trace=True)

        res = scorer.scoreAllRecords()
        self.logSuccess(f"Validation results: {res}")
        
        self.project.gridOutput = res