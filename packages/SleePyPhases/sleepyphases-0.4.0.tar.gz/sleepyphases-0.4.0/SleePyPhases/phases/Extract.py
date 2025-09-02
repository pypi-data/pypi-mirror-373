from pathlib import Path
import numpy as np
from pyPhases import Phase
from pyPhases.util import BatchProgress
from pyPhasesRecordloader import AnnotationNotFound, ChannelsNotPresent, ParseError, RecordLoader

from SleePyPhases.FeatureExtraction import FeatureExtraction
from SleePyPhases.PreManipulation import PreManipulation
from SleePyPhases.PSGEventManager import PSGEventManager
from SleePyPhases.SignalPreprocessing import SignalPreprocessing


class RecordProcessor:
    """this class is needed to tailor the multithreading"""

    def __init__(
        self,
        recordLoader,
        preProcessingConfig,
        signalProcessing,
        eventManager,
        labelChannels,
        project=None,
    ) -> None:
        self.recordLoader = recordLoader
        self.preProcessingConfig = preProcessingConfig
        self.signalProcessing = signalProcessing
        self.eventManager = eventManager
        self.labelChannels = labelChannels
        self.channelNotPresent = []
        self.project = project

    def prepareLabelSignal(self, name, eventSignal, signalLength):

        labelSignalArray = np.zeros(signalLength)
    
        if name == "SleepArousals":
            if "arousal" in eventSignal:
                eventSignal = eventSignal["arousal"]
                labelSignalArray[eventSignal > 1] = 1
        elif name == "SleepStagesAASM":
            if "sleepStage" not in eventSignal:
                raise ChannelsNotPresent("sleepStage")
            eventSignal = eventSignal["sleepStage"]
            labelSignalArray[eventSignal == PSGEventManager.INDEX_WAKE] = 0
            labelSignalArray[eventSignal == PSGEventManager.INDEX_REM] = 1
            labelSignalArray[eventSignal == PSGEventManager.INDEX_NREM1] = 2
            labelSignalArray[eventSignal == PSGEventManager.INDEX_NREM2] = 3
            labelSignalArray[eventSignal == PSGEventManager.INDEX_NREM3] = 4
        elif name == "SleepApnea":
            if "apnea" in eventSignal:
                eventSignal = eventSignal["apnea"]
                labelSignalArray[:] = 0
                labelSignalArray[eventSignal == PSGEventManager.INDEX_APNEA_OBSTRUCTIVE] = 1
                labelSignalArray[eventSignal == PSGEventManager.INDEX_APNEA_MIXED] = 2
                labelSignalArray[eventSignal == PSGEventManager.INDEX_APNEA_CENTRAL] = 3
                labelSignalArray[eventSignal == PSGEventManager.INDEX_APNEA_HYPO] = 4
        elif name == "SleepLegMovements":
            if "limb" in eventSignal:
                eventSignal = eventSignal["limb"]
                labelSignalArray[:] = 0
                labelSignalArray[eventSignal > 1] = 1
        elif name == "SleepCombined":
            if "sleepStage" not in eventSignal:
                raise ChannelsNotPresent("sleepStage")
            labelSignalArray = np.zeros((signalLength, 4))
            labelSignalArray[:, 0] = self.prepareLabelSignal("SleepStagesAASM", eventSignal, signalLength)
            labelSignalArray[:, 1] = self.prepareLabelSignal("SleepArousals", eventSignal, signalLength)
            labelSignalArray[:, 2] = self.prepareLabelSignal("SleepApnea", eventSignal, signalLength)
            labelSignalArray[:, 3] = self.prepareLabelSignal("SleepLegMovements", eventSignal, signalLength)
        else:
            raise Exception("unknown label channel: " + name)
        return labelSignalArray

    def preparelabelChannels(self, eventSignal, signalLength):
        labelChannels = []
        for name in self.labelChannels:
            signal = self.prepareLabelSignal(name, eventSignal, signalLength)
            signal = signal.reshape(-1, 1)
            labelChannels.append(signal)

        return np.concatenate(labelChannels, axis=1)

    @staticmethod
    def tailorToSleepScoring(recordSignal, events, useSPT=False, fillLastSleepstage=False, addOffset=None, cutToAnnotation=False):
        sleepEventNames = ["R", "N1", "N2", "N3"]
        allSleepStages = ["W", "undefined"] + sleepEventNames
        offsetStart = None
        offsetEnd = None
        addOffset = addOffset or [0, 0]


        if not useSPT:
            # add wake to relevant stages to cut only undefined
            sleepEventNames = allSleepStages
            ligthEvents = [e for e in events if e.name in ["lightOn", "lightOff"]]
            if lightOff := [e for e in ligthEvents if e.name == "lightOff"]:
                offsetStart = lightOff[0].start

            if lightOn := [e for e in ligthEvents if e.name == "lightOn"]:
                offsetEnd = lightOn[0].start

        sleepEvents = [e for e in events if e.name in sleepEventNames]
        allSleepEvents = [e for e in events if e.name in allSleepStages]

        if not sleepEvents:
            raise ChannelsNotPresent("SleepStagesAASM")

        startOffset = sleepEvents[0].start if offsetStart is None else offsetStart
        if sleepEvents[-1].duration == 0:
            sleepEvents[-1].duration = len(recordSignal) / recordSignal.targetFrequency - sleepEvents[-1].start if fillLastSleepstage else 30
        endOffset = sleepEvents[-1].end() if offsetEnd is None else offsetEnd

        if startOffset == 0 and endOffset is None:
            return events

        startOffset += addOffset[0]
        endOffset += addOffset[1]

        startOffset = max(allSleepEvents[0].start, startOffset)
        endOffset = min(allSleepEvents[-1].end(), endOffset)

        # if the signal is shorter than sleep annotation, cut the events and smooth to 30 seconds
        if cutToAnnotation:
            _, maxSignalLength = recordSignal.getShape()
            if endOffset * recordSignal.targetFrequency > maxSignalLength:
                endOffset = maxSignalLength / recordSignal.targetFrequency
                endOffset = int(endOffset / 30) * 30
        
        recordSignal.signalOffset(startOffset, endOffset)

        newEvents = []
        for event in events:
            if startOffset > 0:
                if event.end() <= startOffset:
                    continue
                if event.start < startOffset:
                    event.duration -= startOffset - event.start
                    event.start = 0
                else:
                    event.start -= startOffset
            if endOffset is not None:
                if event.start >= endOffset - startOffset:
                    continue
                if event.end() > endOffset - startOffset:
                    event.duration -= event.end() - endOffset + startOffset
            newEvents.append(event)

        if not event:
            raise ChannelsNotPresent("Arousals")

        return newEvents

    def __call__(self, recordId):
        try:
            recordSignal, events = self.recordLoader.loadRecord(recordId)

            targetSignals = self.preProcessingConfig["targetChannels"]
            targetFrequency = self.preProcessingConfig["targetFrequency"]
            labelFrequency = self.preProcessingConfig["labelFrequency"]
            featureChannels = self.preProcessingConfig["featureChannels"]
            manipulationSteps = self.preProcessingConfig["manipulationSteps"]
            recordSignal.targetFrequency = targetFrequency

            # set the target frequency for the signal to get the correct signal length
            self.signalProcessing.preprocessingSignal(recordSignal)

            recordSignal, events = PreManipulation.getInstance(manipulationSteps)(recordSignal, events)
            FeatureExtraction.getInstance(self.project).extractChannelsByConfig(recordSignal, featureChannels)

            signalLength = round(recordSignal.getSignalLength() * labelFrequency / targetFrequency)
            eventSignal = self.eventManager.getEventSignalFromList(
                events,
                signalLength,
                targetFrequency=labelFrequency,
                forceGapBetweenEvents=False,
            )
            # signalLength * 30
            eventSignal = self.preparelabelChannels(eventSignal, signalLength)
            processedSignal = recordSignal.getSignalArray(targetSignals)
        except ChannelsNotPresent as e:
            self.channelNotPresent.append(e.channels)
            print(f"\033[31;1;4m%s\033[0mChannel missing in {recordId}: {e.channels} ... skipping record")
            return None
        except AnnotationNotFound as e:
            self.channelNotPresent.append(e.name)
            print(f"\033[31;1;4m%s\033[0mAnnotation missing in {recordId}: {e.name} ... skipping record")

            return None
        except ParseError as e:
            print(f"\033[31;1;4m%s\033[0mParseError in record {recordId}, record will be skipped: {e}")
            return None
        
        return processedSignal, eventSignal


class Extract(Phase):
    """
    Extract numpy arrays from the raw records in the dataset
    """

    useMultiThreading = True
    threads = None

    def getRecordProcessor(self):
        preprocessingConfig = self.getConfig("preprocessing")
        processRecord = RecordProcessor(
            recordLoader=RecordLoader.get(),
            preProcessingConfig=preprocessingConfig,
            signalProcessing=SignalPreprocessing.getInstance(preprocessingConfig),
            eventManager=PSGEventManager(),
            labelChannels=self.getConfig("labelChannels"),
            project=self.project,
        )
        return processRecord

    def extractRecord(self, recordId):
        
        processRecord = self.getRecordProcessor()
        result = processRecord(recordId)      
        if result is None:
            raise ChannelsNotPresent(processRecord.channelNotPresent)
        return result

    def buildFromRecords(self, records, force=False):
        processRecord = self.getRecordProcessor()
        exporterSignals, dataIdSignals = self.project.getExporterAndId("data-processed", np.memmap)
        exporterFeatures, dataIdFeatures = self.project.getExporterAndId("data-features", np.memmap)
        exporterSignals.options["dtype"] = self.getConfig("preprocessing.dtype", "float32")
        exporterFeatures.options["dtype"] = self.getConfig("preprocessing.dtype", "float32")

        removedRecordIds = []
        removed_records_path = exporterSignals.getPath(f"{dataIdSignals}-removed-records-tmp.npy")
        
        if force is False:
            if exporterSignals.exists(dataIdSignals) and exporterFeatures.exists(dataIdFeatures):
                self.logSuccess("Datafiles already exist")
                return []

            if exporterSignals.existsTmp(dataIdSignals) and exporterFeatures.existsTmp(dataIdFeatures):
                exporterSignals.loadTmp(dataIdSignals)
                exporterFeatures.loadTmp(dataIdFeatures)
                
                if Path(removed_records_path).exists():
                    removedRecordIds = np.load(removed_records_path, allow_pickle=True).tolist()

                recordsLoaded = len(exporterFeatures.currentArrayShapes[dataIdSignals][0])
                total_processed = recordsLoaded + len(removedRecordIds)
                
                # Skip both successfully processed and removed records
                records = records[total_processed:]
                self.logSuccess(f"Resuming extraction: {recordsLoaded} records already loaded, {len(removedRecordIds)} records skipped, {len(records)} to go")

        bp = BatchProgress(records)
        bp.useMultiThreading = self.useMultiThreading
        if self.threads is not None:
            bp.threads = self.threads

        def combine(recordList, dataIndex):
            recordList = recordList.copy()
            # append the the data and the shape to a tmp file

            # check if all records where loaded, else extend the removedRecord list
            if None in recordList:
                rm = [i + dataIndex for i, r in enumerate(recordList) if r is None]
                new_removed = [records[r] for r in rm]
                removedRecordIds.extend(new_removed)
                np.save(removed_records_path, removedRecordIds)
                
                recordList = [r for r in recordList if r is not None]
                self.logWarning("Skipped %i records: channels/annotation not present" % len(rm))

            if len(recordList) > 0:
                signals, features = zip(*recordList)
                exporterSignals.saveAndAppendArray(dataIdSignals, signals)
                exporterFeatures.saveAndAppendArray(dataIdFeatures, features)

        bp.start(processRecord, afterBatch=combine)

        # save the tmp files to the final files
        if not exporterSignals.exists(f"{dataIdSignals}-tmp"):
            raise Exception("No record was stored during the extraction, please check logs for skipped records")
        exporterSignals.finishStream(dataIdSignals)
        exporterFeatures.finishStream(dataIdFeatures)

        return removedRecordIds

    def generateData(self, name):
        
        # unregister modelstate in case gpu memory is needed for extraction
        if self.project.dataExists(self.project.getDataFromName("modelState")):
            self.project.unregister("modelState")

        if name == "record-preprocessed":
            recordId = self.getConfig("recordId")
            return self.extractRecord(recordId)
        elif name[:5] == "data-":
            groupedRecords = self.project.getData("allDBRecordIds", list)
            flatten_ids = [r for ids in groupedRecords.values() for r in ids]

            removedRecordIds = self.buildFromRecords(flatten_ids)

            signals = self.getData("data-processed", np.memmap, generate=False)
            features = self.getData("data-features", np.memmap, generate=False)

            self.registerData("data-processed", signals)
            self.registerData("data-features", features)
            self.registerData("removedRecordIds", removedRecordIds)

    def main(self):
        self.generateData("data-processed")
