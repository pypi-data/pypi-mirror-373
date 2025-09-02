from typing import List
from pyPhases import Phase
from tqdm import tqdm
import pandas as pd

from pyPhasesRecordloader import AnnotationNotFound, RecordLoader, ChannelsNotPresent, Event, ParseError

from SleePyPhases.RecordFeatureExtraction import RecordFeatureExtraction
from SleePyPhases.SleepMetaData import SleepMetaData

class ExtractFeatures(Phase):
    allowTraining = False
    features = None

    def getChannelMetadata(self, recordId):
        recordLoader = RecordLoader.get()
        recordLoader.getSignalHeaders(recordId)

    def getRecordMetadata(self, recordId):
        recordLoader = RecordLoader.get()
        datasetConfig = self.getConfig("dataversion")
        metaData = {
            "recordId": recordId,
            "annotationExist": recordLoader.existAnnotation(recordId),
        }
        channelMetadata = []
        headers = recordLoader.getSignalHeaders(recordId)

        for header in headers:
            channelMetadata.append({
                "recordId": recordId,
                "channel": header["name"],
                "sample_rate": header["sample_rate"]
            })

        # if metaData["annotationExist"]:
        #     recordMetadata = recordLoader.getMetaData(recordId)
        #     metaData.update(recordMetadata)
        # else:
        #     self.logError(f"record id {recordId} does not exist")

        # if metaData["annotationExist"] and "minimalSamplingRate" in datasetConfig and datasetConfig["minimalSamplingRate"] is not None:
        #     minimalSamplingRates = datasetConfig["minimalSamplingRate"]

        #     try:
        #         headers = recordLoader.getSignalHeaders(recordId)

        #         for header in headers:
        #             typeStr = header["type"]
        #             if typeStr in minimalSamplingRates and header["sample_rate"] < minimalSamplingRates[typeStr]:
        #                 self.logError(f"record id {recordId} exluded because of minimal sampling rate for {typeStr}")
        #                 metaData["samplingRateCheck"] = False
        #                 break
        #     except ChannelsNotPresent as e:
        #         self.logError(f"record id {recordId} exluded because channels missinng {e.channels}")
        #         metaData["channelMissing"] = e.channels
        # return metaData
    
    def getFeature(self, name, recordId, options={}, channelType=None):
        recordLoader=RecordLoader.get()
        recordLoader.ignoreTargetSignals = True
        features = None
        recordDf = self.getData("metadata", pd.DataFrame)
        recordEntry = recordDf.loc[recordId]

        eventDf = self.getData("metadata-events", pd.DataFrame)

        featureExistName = f"feature-{name}"
        featureExist = featureExistName in recordDf.columns
        if not featureExist:
            recordDf[featureExistName] = False
        elif recordEntry[featureExistName]:
            return eventDf.query(f"recordId == '{recordId}' and feature == '{name}'")

        # calcluate Features
        try:
            recordSignal = recordLoader.getHarmonizedSignal(recordId)

            events: List[Event] = RecordFeatureExtraction.getInstance().step(name, recordSignal, *options)

            if channelType is not None:
                channelType = [s.name for s in recordSignal.signals if s.typeStr == channelType]
            else:
                channelType = [None]
                events = [events]

            eventList = []
            for index, ev in enumerate(events):
                eventList += [
                    {
                        "recordId": recordId,
                        "channel": channelType[index],
                        "feature": name,
                        "event": e.name,
                        "start": e.start,
                        "duration": e.duration
                    } for e in ev
                ]
            featureDf = pd.DataFrame(eventList)
            eventDf = pd.concat((eventDf, featureDf))
            self.registerData("metadata-events", eventDf)
            recordDf.loc[recordId, featureExistName] = True
            self.registerData("metadata", recordDf)

            return eventDf

            # features = FeatureExtraction(self.project).step(name, recordSignal)
        except ChannelsNotPresent as e:
            self.logError(f"channels not present: {e.channels}")
            pass

        return None
        

    def getSomnometrics(self, name, recordId):
        metricConfig = self.getConfig(f"somnometrics.{name}", {})
        metricType = metricConfig["type"] if "type" in metricConfig else "recordFeature"

        metadataRecords = self.getData("metadata", pd.DataFrame)
        metaDataChannels = self.getData("metadata-channels", pd.DataFrame)

        # metadataRecords = pd.DataFrame.from_records(metadataRecords, index="recordId")
        # metaDataChannels = pd.DataFrame.from_records(metaDataChannels)
 
        if recordId not in metadataRecords.index:
            recordMetadata = self.getRecordMetadata(recordId)
            metadataRecords = metadataRecords.append(recordMetadata)
            self.registerData("metadata", metadataRecords)
        else:
            recordMetadata = metadataRecords.query(f"recordId == '{recordId}'")

        lookupDf = metaDataChannels if metricType == "recordChannel" else metadataRecords
        metaDataEntries = lookupDf.query(f"recordId == '{recordId}'")
            
        sm = SleepMetaData()
        if name not in metaDataEntries.columns:
            metricConfig = self.getConfig("somnometrics")[name]
            options = metricConfig["options"] if "options" in metricConfig else {}
            channelType = metricConfig["channelType"] if "channelType" in metricConfig else {}
            
            featureNames = metricConfig["features"]

            for featureName in featureNames:
                featureList = self.getFeature(featureName, recordId, options, channelType=channelType)

                sm.addFeatureList(featureName, featureList)

        return sm.getMetaData(name)

    # featureConfigs is a dict with feature names as keys, so that if they exist this method is not called and loaded from the feature table directly
    # if there is no featureConfig all features will be calculated for a record, to optimize the record loading
    # feature name is used to recalculate the feature, so it will always return the full recording row, but only recalculate if the feature is not present
    def generateData(self, dataId, recordId=None, channel=None, recalculate=True, **featureNameDict):
        if dataId != "features":
            raise Exception(f"data id {dataId} not supported")

        if recordId is None:
            # self.features = pd.DataFrame(columns=["recordId", "channel"]).set_index(["recordId", "channel"], drop=False)
            self.features = pd.DataFrame(index=pd.MultiIndex(levels=[[],[]], codes=[[],[]], names=['recordId','channel']))
            self.registerData("features", self.features, save=False)
            return self.features

        if self.features is None:
            self.features = self.getData("features", pd.DataFrame)

        featureConfigs = self.getConfig("featureExtraction.features", [])
        if featureNameDict != {}:
            featureNames = list(featureNameDict.keys())
            featureConfigs = [f for f in featureConfigs if f["name"] in featureNames]

        recordLoader = RecordLoader.get()
        recordSignal = None
        try:
            recordSignal, eventlist = recordLoader.loadRecord(recordId)
        except AnnotationNotFound as e:
            self.logError(f"Annotation missing in {recordId}: {e.name} ... skipping record")
        except ChannelsNotPresent as e:
            self.logError(f"Channels missing in {recordId}: {e.channels} ... skipping record")
        except ParseError as e:
            self.logError(f"ParseError in record {recordId}, record will be skipped: {e}")

            
        for featureConfig in featureConfigs:
            if recordSignal is None:
                self.features.loc[recordId, "recordId"] = recordId
                self.features.loc[recordId, featureConfig["name"]] = True
                self.registerData("features", self.features)
                return {}
            
            channels = featureConfig["channels"] if channel is None else [channel]
            for c in channels:
                try:
                    idx = (recordId, c)
                    featureStep = featureConfig["type"]
                    RecordFeatureExtraction.getInstance().updateMetadataByStep(featureStep, recordSignal, eventlist, metadata=self.features, channel=c)
                except ChannelsNotPresent as e:
                    self.logError(f"channels not present: {e.channels}")

                self.features.loc[idx, "recordId"] = recordId
                self.features.loc[idx, "channel"] = c
                self.features.loc[idx, featureConfig["name"]] = True
        
        self.registerData("features", self.features)
        idx = (recordId, channel) if channel is not None else recordId
        return self.features.loc[idx]

    def main(self):
        import pandas as pd
        self.features = None
        metadata = self.project.getData("metadata", pd.DataFrame)
        recordIds = metadata["recordId"]
        forceCalculation = self.getConfig("featureExtraction.force", False)

        reqFeatures = {f["name"]: True for f in self.getConfig("featureExtraction.features", [])}

        recordId = self.getConfig("recordId", False)
        recordIds = [recordId] if recordId else recordIds.iloc

        for recordId in tqdm(recordIds.iloc):
            if forceCalculation:
                # the parameter forced has no meaning, it is just known to be not in the metadata, so the record will always be recalculated
                reqFeatures["forced"] = True # should never be found
            rows = self.getData("features", pd.DataFrame, recordId=recordId, **reqFeatures)
            if len(rows) == 0:
                self.logError(f"no features for {recordId}")
                
