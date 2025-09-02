from pyPhases import Data, PluginAdapter, Project
from pyPhasesRecordloader import RecordLoader

from SleepHarmonizer.recordwriter.RecordWriter import RecordWriter

from SleePyPhases.phases.ExtractFeatures import ExtractFeatures
from SleePyPhases.phases.Extract import Extract
from SleePyPhases.phases.Setup import Setup
from SleePyPhases.phases.BuildDataset import BuildDataset
from SleePyPhases.phases.Training import Training
from SleePyPhases.phases.Validation import Validation
from SleePyPhases.phases.Eval import Eval
from SleePyPhases.phases.EvalReport import EvalReport
from SleePyPhases.phases.ThresholdOptimisation import ThresholdOptimisation
from SleePyPhases.phases.TestRun import TestRun
from SleePyPhases.phases.ExtractFeatures import ExtractFeatures


from pyPhases.exporter.PickleExporter import PickleExporter
from pyPhases.exporter.PandasExporter import PandasExporter
from pyPhasesML.exporter.ModelExporter import ModelExporter
from pyPhasesML.exporter.MemmapRecordExporter import MemmapRecordExporter


class Plugin(PluginAdapter):
    def __init__(self, project: Project, options=None):
        super().__init__(project, options)

        phaseMap = {
            "Setup": (Setup, ["dataversionmanager"]),
            "Extract": (Extract, ["removedRecordIds", "data-processed", "data-features", "record-preprocessed"]),
            "BuildDataset": (BuildDataset, ["dataset-training", "dataset-validation", "dataset-test", "dataset-bySplit", "record-data"]),
            "Training": (Training, ["modelState", "modelStateConfig"]),
            "Validation": (Validation, []),
            "ThresholdOptimisation": (ThresholdOptimisation, ["threshold", "validationResult"]),
            "Eval": (Eval, ["evalResults", "eventResults"]),
            "EvalReport": (EvalReport, []),
            "ExtractFeatures": (ExtractFeatures, ["features"]),
            "TestRun": (TestRun, []),
        }
        dataMap = {
            "features": ["metadata"],
            "events": ["allDBRecordIds"],
            "data-processed": ["allDBRecordIds", "preprocessing", "labelChannels"],
            "record-preprocessed": ["recordId", "data-processed"],
            "record-data": [],
            "data-features": ["data-processed"],
            "dataversionmanager": ["data-processed", "datafold", "dataversion"],
            "removedRecordIds": ["data-processed"],
            "modelState": ["dataset-bySplit", "modelName", "model", "inputShape", "segmentManipulation", "trainingParameter", "fold"],
            "modelStateConfig": ["modelState"],
            "threshold": ["modelState", "eventEval", "thresholdMetric", "fixedThreshold"],
            "validationResult": ["modelState", "segmentManipulationEval", "thresholdMetric", "optimizeOn"],
            "evalResults": ["threshold", "evalOn", "manipulationAfterPredict", "segmentManipulationEval"],
            "eventResults": ["evalResults", "eventEval"],
            "dataset-bySplit": ["dataversionmanager"],
            "dataset-training": ["dataversionmanager"],
            "dataset-validation": ["dataversionmanager"],
            "dataset-test": ["dataversionmanager", "evalOn"],
        }

        for phaseName, (phaseClass, exportData) in phaseMap.items():
            if phaseName not in self.project.phaseMap:
                exportData = [Data(dataName, self.project, dataMap[dataName]) for dataName in exportData]
                self.project.addPhase(phaseClass(exportData))

        dataPath = project.getConfig("data-path", "./data")

        project.registerExporter(PickleExporter({"basePath": dataPath}))
        project.registerExporter(PandasExporter({"basePath": dataPath}))
        project.registerExporter(ModelExporter({"basePath": dataPath}))
        project.registerExporter(MemmapRecordExporter({"basePath": dataPath}))



