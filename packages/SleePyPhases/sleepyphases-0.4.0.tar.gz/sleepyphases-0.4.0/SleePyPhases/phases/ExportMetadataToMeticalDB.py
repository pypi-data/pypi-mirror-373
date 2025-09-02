
from itertools import chain
from pyPhases import Phase
from tqdm import tqdm

from pyPhasesRecordloader import AnnotationNotFound, ChannelsNotPresent, ParseError

class ExportMetadataToMeticalDB(Phase):
    """export extracted metadata from psg files to the patient db"""

    exportTo = "db"

    def main(self):
        import pandas as pd
        from pypika import PostgreSQLQuery, Schema
        from SleepHarmonizer.recordloaders.AliceTextReportLoader import AliceTextReportLoader

        from SleePyPhases.recordloaders.MedicalDB import MedicalDB

        metadata = self.getData("metadata", pd.DataFrame)
        relevantCols = [v for v in AliceTextReportLoader.relevantRows.values() if v != ""]
        channelMetaData = self.getData("metadata-channels", pd.DataFrame)

        featureData = self.getData("features", pd.DataFrame)
        MedicalDB.config = self.getConfig("medicalDB")
        medDB = MedicalDB.get()
        medDB.connect()
        schema = Schema(self.getConfig("medicalDB.schema"))

        patientTable = schema.patient
        caseTable = schema.medical_case
        recordTable = schema.record
        recordMetaTable = schema.record_somnometric
        channelTable = schema.channel
        channelMetaTable = schema.channel_somnometric
        somnoemetricTable = schema.somnometric_type
        
        for rowIndex, row in tqdm(metadata.iterrows(), total=len(metadata)):
            channelData = channelMetaData.query(f"recordId == '{rowIndex}'")
            features = featureData.query(f"recordId == '{rowIndex}'")

            missingCaseCounts = {}
            def getMissingCid(pid):
                if pid in missingCaseCounts:
                    missingCaseCounts[pid] += 1
                else:
                    missingCaseCounts[pid] = 0
                return "missing_%s_%s" % (pid, missingCaseCounts[pid]) 
            
            patientId = row["patient"] if "patient" in row and not pd.isna(row["patient"]) else "missing_%s" % rowIndex
            caseId = row["case"] if "case" in row and not pd.isna(row["case"]) else getMissingCid(patientId)
            recordId = row["recordId"]
            
            recordEntries = {
                "recordId": "id_record", 
                "start": "start", 
                "dataCount": "data_count",
                "psg_setup": "psg_config",
                "lightOff": "light_off",
                "lightOn": "light_on",
            }
            removeEntries = ["annotationExist", "channelMissing", "samplingRateCheck"]
            removeEntries += ["diagnoses", "normalbefund", "diagnosen_rdi_lt5_lt15", "sbas_nachrdi_lt5_lt15", "andere_hinweise", "sonstige", "rbd", "hypersomnie", "insomnie", "rls_plmd"]
            removeEntries += ["startRecord", "comment"]
            removeEntries += ["age", "gender"]
            removeEntries += ["case", "patient", "psg_type"]

            dateEntries = ["start"]

            for d in dateEntries:
                if pd.notna(row.loc[d]):
                    row.at[d] = row.loc[d].isoformat()      
                          
            for r in removeEntries:
                if r in row:
                    del row[r]

            record = {target: row[src] for src, target in recordEntries.items() if src in row and not pd.isna(row[src])}

            for src,target in recordEntries.items():
                if src in row:
                    del row[src]

            # insert patient information
            q = PostgreSQLQuery.into(patientTable)\
                .columns(patientTable.id_patient)\
                .insert(patientId)\
                .on_conflict().do_nothing()
            medDB.execute(str(q))

            # insert case information
            q = PostgreSQLQuery.into(caseTable)\
                .columns("id_medical_case", "id_patient")\
                .insert(caseId, patientId)\
                .on_conflict().do_nothing()
            medDB.execute(str(q))

            # insert record information
            record["id_medical_case"] = caseId 
            q = PostgreSQLQuery.into(recordTable)\
                .columns(*list(record.keys()))\
                .insert(*list(record.values()))\
                .on_conflict(recordTable.id_record)
            
            for col, val in record.items():
                if col != "id_record" and not pd.isna(val):
                    q = q.do_update(col, val)
            medDB.execute(str(q))

            def getTypeAndValue(val):
                if isinstance(val, bool):
                    return "float", 1 if val else 0
                
                dtype = "float" if isinstance(val, float) or val.dtype == float else "string"

                return dtype, val
            
            def addMetricType(metricName, mType):
                
                mType, val = getTypeAndValue(mType)

                q = PostgreSQLQuery.into(somnoemetricTable)\
                    .columns("id_somnometric_type", "valuetype")\
                    .insert(metricName, mType)\
                    .on_conflict("id_somnometric_type")\
                    .do_update("valuetype", mType)
                    # .returning('id_somnometric_type')
                return medDB.execute(str(q))

            # delete all record metadata
            q = PostgreSQLQuery.from_(recordMetaTable)\
                .delete()\
                .where(recordMetaTable.id_record == recordId)
                # where source == psg
            medDB.execute(str(q))

            for metricName in relevantCols:
                if metricName in metadata.columns:
                    addMetricType(metricName, metadata[metricName])
                
            # add all record metadata
            for column, val in row.items():
                if column in relevantCols and not pd.isna(val) and val is not None:
                    typestr, val = getTypeAndValue(row[column])
                    q = PostgreSQLQuery.into(recordMetaTable)\
                        .columns(["id_record", "id_somnometric_type", f"value_{typestr}"])\
                        .insert([recordId, column, val])
                    medDB.execute(str(q))
            
            # add all the metadata types (somnometrics types)
            # channelMetrics = [col for col in channelData.columns if col not in ["label", "signalName", "recordId"]]
            # for metricName in channelMetrics:
                # addMetricType(metricName, channelData[metricName].dtype)

            # delete all chanel data for the reocord
            q = PostgreSQLQuery.from_(channelMetaTable)\
                .using(channelTable)\
                .where(channelMetaTable.id_channel == channelTable.id_channel)\
                .where(channelTable.id_record == recordId)\
                .delete()
            medDB.execute(str(q))
            
            
            q = PostgreSQLQuery.from_(channelTable)\
                .delete()\
                .where(channelTable.id_record == recordId)
            
            medDB.execute(str(q))

            if len(features) > 0:
                featureMetrics = [col for col in features.columns if col not in ["channel", "recordId"]]
                for metricName in featureMetrics:
                    addMetricType(metricName, features[metricName])

            
            for channel in channelData.iloc:
                if "signalName" not in channel:
                    continue
                chanelDict = {
                    "name": channel["signalName"],
                    "frequency": channel["sample_rate"] if "sample_rate" in channel else channel["sample_frequency"], # sample_frequency
                    "prefilter": channel["prefilter"],
                    "physical_max": channel["physical_max"],
                    "physical_min": channel["physical_min"],
                    "digital_max": channel["digital_max"],
                    "digital_min": channel["digital_min"],
                    "transducer": channel["transducer"],
                    "type": channel["type"],
                    "id_record": recordId
                }
                
                q = PostgreSQLQuery.into(channelTable)\
                    .columns(*list(chanelDict.keys()))\
                    .insert(*list(chanelDict.values()))
                channelId = medDB.executeAndFetchOne(f"{q} RETURNING id_channel")[0]


                # add channel specific features
                if len(features) == 0:
                    continue

                channelFeatures = features[features["channel"] == channel["signalName"]]

                if len(channelFeatures) > 0:
                    # each channel/recording should only have a single row
                    channelFeatures = channelFeatures.iloc[0]
                    for feat in featureMetrics:
                        val = channelFeatures[feat]
                        if not pd.isna(val):
                            typestr, val = getTypeAndValue(val)
                            
                            q = PostgreSQLQuery.into(channelMetaTable)\
                                .columns(["id_channel", "id_somnometric_type", f"value_{typestr}"])\
                                .insert([channelId, feat, val])
                            medDB.execute(str(q))


                # q = PostgreSQLQuery.from_(recordMetaTable)\
                #     .delete()\
                #     .where(recordMetaTable.id_somnometric_type == metricName)\
                #     .where(recordMetaTable.id_record == recordId)
                # medDB.execute(str(q))

                # q = PostgreSQLQuery.into(recordMetaTable)\
                #     .columns("id_somnometric_type", "id_record", f"value_{mType}")\
                #     .insert(metricName, recordId, value)
                # medDB.execute(str(q))
            

            # if "channels" not in row:
            #     continue

            # for channel in row["channels"]:
            #     channelName = channel["signalName"]

            #     chanelDict = {
            #         "name": channelName,
            #         "frequency": channel["sample_rate"], # sample_frequency
            #         "prefilter": channel["prefilter"],
            #         "physical_max": channel["physical_max"],
            #         "physical_min": channel["physical_min"],
            #         "digital_max": channel["digital_max"],
            #         "digital_min": channel["digital_min"],
            #         "prefilter": channel["prefilter"],
            #         "transducer": channel["transducer"],
            #         "type": channel["type"],
            #         "id_record": recordId
            #     }
            #     q = PostgreSQLQuery.into(channelTable)\
            #         .columns(*list(chanelDict.keys()))\
            #         .insert(*list(chanelDict.values()))
            #     medDB.execute(str(q))

            # if rowIndex % 25 == 0:
            medDB.commit()
            # table = schema.acq_metadata

            # checkQuery = PostgreSQLQuery.from_(table).select(1).where(table.acquisition_id == metaData['acquisition_id'])
            # medDB.execute(str(checkQuery))
            # exist = medDB.executeAndFetchOne(checkQuery)
            # if exist:
            #     q = PostgreSQLQuery.update(table).where(table.acquisition_id == metaData['acquisition_id'])
            #     for f, v in metaData.items():
            #         q = q.set(f, v)
            # else:
            #     q = PostgreSQLQuery.into(table).columns(existingColumns).insert(values)
            # medDB.execute(q)
        medDB.close()
