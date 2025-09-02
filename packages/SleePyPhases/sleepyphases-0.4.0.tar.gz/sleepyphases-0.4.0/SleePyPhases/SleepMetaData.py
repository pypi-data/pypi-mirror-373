import numpy as np

from pyPhases.util.Logger import classLogger

from SleePyPhases.PSGEventManager import PSGEventManager


@classLogger
class SleepMetaData:
    validationNameIdMap = {}

    def __init__(self):
        self.metaDataMap = {}
        self.metaData = []

    def getEventsFromSignal(self, signal, classification):
        eventmanager = PSGEventManager()
        return [e for e in eventmanager.getEventsFromSignal(signal, classification) if e.name != "None"]


    def getIndexForEventCount(self, eventCount):
        testInMinutes = self.getMetaData("tst", 0, "min")

        if testInMinutes == 0:
            return None

        return eventCount / (testInMinutes / 60)

    def registerMetadata(self, name, value, unit="s"):
        # normalize to minutes, because of alice
        if unit == "s" and value is not None:
            value /= 60
            unit = 'min'

        if name in self.metaDataMap:
            raise Exception("matadata %s allready exist!" % name)

        metaData = {
            "name": name,
            "value": value,
            "unit": unit,
        }

        self.metaDataMap[name] = metaData
        self.metaData.append(metaData)

    def getMetaData(self, name, fallBack=None, unit=None):

        if name not in self.metaDataMap:
            return fallBack

        data = self.metaDataMap[name]
        value = data["value"]
        if data["unit"] == "min" and unit == "s" and value is not None:
            value *= 60

        return value

    def addCountAndIndex(self, name, eventCount):
        self.registerMetadata(f"count{name}", eventCount, unit="#")
        self.registerMetadata(f"index{name}", self.getIndexForEventCount(eventCount), unit="#")

    def addSignal(self, signalName, signal, frequency=1):
        # SleepBin, Arousal, ApneaBin, LMBin

        match signalName:
            case 'Arousal':
                self.fromArousalSignal(signal)
            case 'ApneaBin':
                self.fromApneaSignal(signal, ["None", "respEvent"])
            case 'Apnea4':
                self.fromApneaSignal(signal, ["None", "obstructive/mixed", "central", "hypopnea"])
            case 'LMBin':
                self.fromLegMovementSignal(signal)
            case 'SleepBin':
                self.fromSleepSignalBin(signal, frequency=frequency)
            case 'Sleep4':
                self.fromSleepSignalBin(signal, frequency=frequency)
                self.fromSleepSignalFour(signal, frequency=frequency)

    def fromSleepSignalBin(self, signal, frequency = 1):
        # all time values in seconds
        trt = len(signal) / (frequency)
        tst = sum(signal) / (frequency)
        whereSleep = np.where(signal > 0)[0]
        if len(whereSleep) == 0:
            sLatency = 0
        else:
            if not any(whereSleep):
                sLatency = np.nan
            else:
                sLatency = whereSleep[0] if whereSleep[0] > 0 else whereSleep[1]
                sLatency /= (frequency)


        self.registerMetadata("tst", tst, unit="s")
        self.registerMetadata("spt", trt-sLatency, unit="s")
        self.registerMetadata("trt", trt, unit="s")

        self.registerMetadata("sLatency", sLatency, unit="s")
        self.registerMetadata("waso", trt-sLatency-tst, unit="s")
        self.registerMetadata("sEfficiency", tst / trt * 100, unit="%")

    def fromSleepSignalFour(self, signal, frequency = 1):
        whereREM = np.where(signal == 1)
        rLatency = whereREM[0] - self.getMetaData("sLatency")
        self.registerMetadata("rLatency", rLatency)

    
    def fromApneaSignal(self, signal, classification=None):
        # classification = classification or ["None", "obstructive", "mixed", "central", "hypopnea"]
        events = self.getEventsFromSignal(signal, classification)

        eventCount = len(events)
        self.registerMetadata("countApneaHypopnea", eventCount, unit="#")
        self.registerMetadata("ahi", self.getIndexForEventCount(eventCount))

    def fromArousalSignal(self, signal, classification=None):
        classification = classification or ["None", "Arousal"]
        events = self.getEventsFromSignal(signal, classification)

        self.addCountAndIndex("Arousal", len(events))

    def fromLegMovementSignal(self, signal, classification=None):
        classification = classification or ["None", "LM"]
        events = self.getEventsFromSignal(signal, classification)

        self.addCountAndIndex("PLMS", len(events))
    
    # def calculateMetadata(self, record: Record, registerToRecordAnnotation=None):
    #     self.metaData = []
    #     self.record = record
    #     self.sleepDF = None
    #     self.positionDF = None
    #     self.apneaDF = None
    #     self.apneaHypopneaDF = None
    #     self.arousalDF = None
    #     self.metaDataMap = {}
    #     self.registerToRecordAnnotation = registerToRecordAnnotation

    #     if SleepMetaData.validateRecord is not None:
    #         reportAnnotation = [a for a in self.validateRecord.annotations if a.Annotation_idAnnotation == 3 and a.manual == 1]
    #         reportMetaData = reportAnnotation[-1].data
    #         self.validationMap = {
    #             self.validationNameIdMap[rad.AnnotationData_idAnnotationData]: rad.value for rad in reportMetaData
    #         }

    #     for ra in record.annotations:
    #         if ra.Annotation.name == "NeuroAdultAASMStaging":
    #             self.parseSleepStageEvents(ra)
    #         elif ra.Annotation.name == "RespiratoryEvents":
    #             self.parseRespiratoryEvents(ra)
    #         elif ra.Annotation.name == "BodyPositionState":
    #             self.parseBodyPosition(ra)
    #         elif ra.Annotation.name == "Arousals":
    #             self.parseArousals(ra)
    #         elif ra.Annotation.name == "channelFail":
    #             self.parseChannelFail(ra)
    #         elif ra.Annotation.name == "LegMovementsAASM":
    #             self.parseLegMovements(ra)
    #         elif ra.Annotation.name == "SpO2Events":
    #             self.parseSpO2Events(ra)
    #         elif ra.Annotation.name == "Cardiac":
    #             self.parseCardiacEvents(ra)

    #     return self.metaData

    # def getClassificationEvent(self, df, start, duration):
    #     df

    # def appendDataframe(self, df, dfToAppend, colMap, offsetStart=None, offsetEnd=None):
    #     cols = {n: [] for n in colMap}

    #     if offsetStart is None:
    #         offsetStart = 0

    #     if offsetEnd is None:
    #         offsetEnd = 0

    #     for e in df.iloc:
    #         start = e.start + offsetStart
    #         end = e.end + offsetEnd
    #         possibleEvents = dfToAppend.query("start < %f and end > %f" % (end, start))

    #         for name in cols:
    #             cols[name].append(",".join([ev[colMap[name]] for ev in possibleEvents.iloc]))

    #     for name in cols:
    #         df[name] = cols[name]

    # def appendOffsetSleepStageToEventDF(self, df, offset=-10):
    #     self.appendDataframe(df, self.sleepDF, {"sleepStage%i" % offset: "name"}, offset, offset)

    # def appendSleepStagesToEventDF(self, df):
    #     self.appendDataframe(df, self.sleepDF, {"sleepStage": "name"})

    # def appendBodyPositionsToEventDF(self, df):
    #     self.appendDataframe(df, self.positionDF, {"position": "position"})

    # def getDataFrameForRecordAnnotation(self, ra: RecordAnnotation, nameCol="name"):
    #     return self.getDataFrameForEventList(ra.events, nameCol)

    # def getDataFrameForEventList(self, events, nameCol="name"):
    #     eventList = []

    #     columns = [nameCol, "start", "duration", "end", "amplitude"]
    #     first = True

    #     for event in events:
    #         evlist = [event.name, event.start, event.duration, event.start + event.duration, event.amplitude]

    #         if event.data is not None:
    #             if first:
    #                 columns += list(event.data.keys())
    #                 first = False

    #             evlist += list(event.data.values())

    #         eventList.append(tuple(evlist))

    #     return pd.DataFrame(eventList, columns=columns)

    # def parsePeriodic(self, events, minDiff=5, maxDiff=90, minimumEvents=4):
    #     """
    #     2. The following define a PLM series:
    #         a. The minimum number of consecutive LM events needed to define a PLM series is 4 LMs.
    #         b. The minimum period length between LMs (defined as the time between onsets of consecutive LMs) to include them as part of a PLM series is 5 seconds.
    #         c. The maximum period length between LMs (defined as the time between onsets of consecutive LMs) to include them as part of a PLM series is 90 sec.
    #         d. Leg movements on 2 different legs separated by less than 5 seconds between movement onsets are counted as a single legmovement.
    #     """

    #     plmEvents = []
    #     maxindex = len(events)

    #     if maxindex < 0:
    #         return events

    #     index = 0

    #     lmCountForPLM = 0
    #     while index < maxindex:
    #         startEvent = events.iloc[index]
    #         if index > maxindex:
    #             break

    #         searchIndex = index + 1
    #         isPLM = False
    #         lmCount = 1
    #         curentEvent = startEvent
    #         lmCountWithMinor = 1
    #         lmInPlm = [startEvent.name]

    #         while searchIndex < maxindex:
    #             nextEvent = events.iloc[searchIndex]
    #             diff = nextEvent.start - curentEvent.start

    #             # # if the diff is to small at the beginnging, skip the whole event
    #             # if diff < minDiff and lmCount == 1:
    #             #     break

    #             if diff > maxDiff:
    #                 lmInPlm.append(curentEvent.name)
    #                 break

    #             if diff >= minDiff:
    #                 lmCount += 1
    #                 lmInPlm.append(curentEvent.name)
    #                 curentEvent = nextEvent

    #             lmCountWithMinor += 1

    #             if lmCount >= minimumEvents:
    #                 isPLM = True
    #                 lastPLMEvent = nextEvent
    #                 index = searchIndex

    #             searchIndex += 1

    #         if isPLM:
    #             plmDuration = lastPLMEvent.end - startEvent.start
    #             event = Event("PLM", start=startEvent.start, duration=plmDuration)
    #             event.data = {
    #                 "count": lmCount,
    #                 "countMinor": lmCountWithMinor,
    #                 "countSpan": lmCount,
    #             }
    #             plmEvents.append(event)
    #             lmCountForPLM += event.data["count"]
    #             events.loc[lmInPlm, "inPLM"] = True

    #         index += 1

    #     return self.getDataFrameForEventList(plmEvents)

    # def loadAliceCSV(self, df, csvName="acq_145063167_events.csv", recordStartTime="23:37:14", startInS=1020):
    #     from datetime import datetime, timedelta

    #     recordStart = datetime.strptime(recordStartTime, "%H:%M:%S")
    #     import pandas as pd

    #     alice = pd.read_csv(csvName, sep=";")
    #     df["startTime"] = df.apply(
    #         lambda row: (recordStart + timedelta(seconds=row["start"] + startInS)).strftime("%H:%M:%S"), axis=1
    #     )
    #     alice_lm = alice.query("Typ == 'Beinbewegung'")

    #     # reverse check # should all exist
    #     alice_lm["exist"] = alice_lm.apply(lambda row: len(df.query("startTime == '%s'" % row["Zeit"])), axis=1)
    #     # assert len(alice_lm) == len(alice_lm.query("exist >= 1"))

    #     return alice_lm

    # def parseLegMovements(self, ra: RecordAnnotation):
    #     em = PSGEventManager()
    #     # requires sleep, apnea, arousal

    #     df = self.getDataFrameForRecordAnnotation(ra)

    #     # duration between 0.5 and 10, not around 0.5s apnea/hyponea, not around rera
    #     query = 'name == "LM" and duration >= 0.49 and duration <= 10.1'

    #     # remove all events that start 15 Second around Wake (Alice)
    #     if self.sleepDF is not None:
    #         em.appendDataframe(df, self.sleepDF, colMap={"sleepStage-15": "name"}, offsetStart=-15, fixedDuration=15)
    #         df = self.filterWake(df, "sleepStage-15")

    #     if self.apneaHypopneaDF is not None:
    #         # no apnea/hypopnea within 0.5 Seconds
    #         em.appendDataframe(df, self.apneaHypopneaDF, colMap={"apnea": "name"}, offsetStart=-0.5, offsetEnd=0.5)
    #         query += ' and apnea == ""'

    #     if self.arousalDF is not None:
    #         # associate an arousal within 0.5 Seconds
    #         em.appendDataframe(df, self.arousalDF, colMap={"arousal": "name"}, offsetStart=-0.5, offsetEnd=0.5)
    #         query += ' and arousal != "arousal_rera" and arousal != "RERA"'

    #     df["inPLM"] = False
    #     lm = df.query(query)

    #     plms = self.parsePeriodic(lm)
    #     lmInPLM = lm.query("inPLM == True")

    #     # Debug
    #     # lm["diffToNext"] = False
    #     # lm["diffToNext"].iloc[0:-1] = lm.iloc[1:]["start"].to_numpy() -  lm.iloc[0:-1]["end"].to_numpy()
    #     # lm["diffOnset"] = False
    #     # lm["diffOnset"].iloc[0:-1] = lm.iloc[1:]["start"].to_numpy() -  lm.iloc[0:-1]["start"].to_numpy()
    #     # lm["wouldCount"] = False
    #     # lm["wouldCount"][lm.query("diffOnset >= 5 and diffOnset <= 90").index] = True

    #     if self.arousalDF is not None:
    #         # associate arousals to plmns
    #         em.appendDataframe(plms, self.arousalDF, colMap={"arousal": "name"}, offsetStart=-0.5, offsetEnd=0.5)

    #     tst = self.getMetaData("tst")

    #     self.registerMetadata("countPlms", len(plms), "#")
    #     self.registerMetadata("countLmInPlm", len(lmInPLM), "#")

    #     if self.arousalDF is not None:
    #         plmsWithArousals = plms.query("arousal != ''")
    #         lmInPLMArousal = lmInPLM.query("arousal != ''")

    #         self.registerMetadata("countPlmsArousal", len(plmsWithArousals), "#")
    #         self.registerMetadata("countLmInPlmArousal", len(lmInPLMArousal), "#")

    #         # 4. PLMS arousal index (PLMSArI; PLMS with arousals × 60 / TST) RECOMMENDED
    #         if tst is not None:
    #             self.registerMetadata("indexPlmsArousal", self.getIndexForEventCount(len(plmsWithArousals)), "#/h")
    #             self.registerMetadata("indexLmInPlmsArousal", self.getIndexForEventCount(len(lmInPLMArousal)), "#/h")

    #     if tst is not None:
    #         self.registerMetadata("indexPlms", self.getIndexForEventCount(len(plms)), "#/h")
    #         self.registerMetadata("indexLmInPlmns", self.getIndexForEventCount(len(lmInPLM)), "#/h")

    #     # 1. Number of periodic limb movements of sleep (PLMS) RECOMMENDED -> countLmInPlm
    #     # 2. Number of periodic limb movements of sleep (PLMS) with arousals RECOMMENDED -> countLmInPlmArousal
    #     # 3. PLMS index (PLMSI; PLMS × 60 / TST) RECOMMENDED -> indexLmInPlmns
    #     # 4. PLMS arousal index (PLMSArI; PLMS with arousals × 60 / TST) RECOMMENDED -> indexLmInPlmsArousal

    # def parseChannelFail(self, ra: RecordAnnotation):
    #     df = self.getDataFrameForRecordAnnotation(ra, "failed")
    #     self.failedDF = df

    # def getRecordLength(self):
    #     return self.record.dataCount

    # def parseBodyPosition(self, ra: RecordAnnotation):
    #     df = self.getDataFrameForRecordAnnotation(ra, "position")
    #     self.positionDF = df

    #     em = PSGEventManager()

    #     bodySignal = em.getEventSignalFromDF(df, self.record.dataCount, targetFrequency=1, eventName="position")["bodyposition"]

    #     supine = df.query("position == 'Supine'")
    #     up = df.query("position == 'Up'")
    #     left = df.query("position == 'Left'")
    #     right = df.query("position == 'Right'")
    #     prone = df.query("position == 'Prone'")

    #     self.registerMetadata("countSupine", len(supine), unit="#")
    #     self.registerMetadata("countUp", len(up), unit="#")
    #     self.registerMetadata("countLeft", len(left), unit="#")
    #     self.registerMetadata("countRight", len(right), unit="#")
    #     self.registerMetadata("countProne", len(prone), unit="#")

    #     self.registerMetadata("positionSupine", supine["duration"].sum(), unit="s")
    #     self.registerMetadata("positionUp", up["duration"].sum(), unit="s")
    #     self.registerMetadata("positionLeft", left["duration"].sum(), unit="s")
    #     self.registerMetadata("positionRight", right["duration"].sum(), unit="s")
    #     self.registerMetadata("positionProne", prone["duration"].sum(), unit="s")

    #     if self.sleepDF is not None:

    #         sleepSignal = em.getEventSignalFromDF(self.sleepDF, self.record.dataCount, targetFrequency=1)["sleepStage"]

    #         sleepSignal = sleepSignal > PSGEventManager.INDEX_WAKE
    #         bodySleepSignal = bodySignal[sleepSignal]

    #         sleepPosition = em.getEventsFromSignal(bodySleepSignal, em.eventGroups["bodyposition"], potentiate=True)
    #         sleepPosition = self.getDataFrameForEventList(sleepPosition)
    #         supineSleep = sleepPosition.query("name == 'Supine'")
    #         leftSleep = sleepPosition.query("name == 'Left'")
    #         rightSleep = sleepPosition.query("name == 'Right'")
    #         proneSleep = sleepPosition.query("name == 'Prone'")

    #         self.registerMetadata("positionSupineSleep", supineSleep["duration"].sum(), unit="s")
    #         self.registerMetadata("positionLeftSleep", leftSleep["duration"].sum(), unit="s")
    #         self.registerMetadata("positionRightSleep", rightSleep["duration"].sum(), unit="s")
    #         self.registerMetadata("positionProneSleep", proneSleep["duration"].sum(), unit="s")

    #         posDuration = lambda p: df.query("position == '%s'" % p)["duration"].sum()
    #         posDurationSleep = lambda p: sleepPosition.query("name == '%s'" % p)["duration"].sum()
    #         getSleepPercentage = lambda p: (1 - (posDuration(p) - posDurationSleep(p)) / posDuration(p)) * 100

    #         tst = self.getMetaData("tst")
    #         assert sleepPosition["duration"].sum() == tst, "TST (%f) does not fit the sum of sleeping position duration: %f" % (
    #             tst,
    #             sleepPosition["duration"].sum(),
    #         )
    #         self.registerMetadata("percentageSupineTST", getSleepPercentage("Supine"), unit="%")
    #         self.registerMetadata("percentageLeftTST", getSleepPercentage("Left"), unit="%")
    #         self.registerMetadata("percentageRightTST", getSleepPercentage("Right"), unit="%")
    #         self.registerMetadata("percentageProneTST", getSleepPercentage("Prone"), unit="%")

    # def filterWake(self, df, sleepStageName="sleepStage"):
    #     if len(df) == 0:
    #         return df
    #     return df[df[sleepStageName].str.contains("W").eq(False)]

    # def filterRemTrue(self, df):
    #     if len(df) == 0:
    #         return df
    #     return df[df["sleepStage"].str.contains("R").eq(True)]

    # def filterNremTrue(self, df):
    #     if len(df) == 0:
    #         return df
    #     return df[df["sleepStage"].str.contains("N").eq(True)]

    # def getIndexForEventCount(self, eventCount):
    #     tst = self.getMetaData("tst")

    #     if tst is None:
    #         return None

    #     return eventCount / tst * 60 * 60

    # def parseRespiratoryEvents(self, ra: RecordAnnotation):
    #     df = self.getDataFrameForRecordAnnotation(ra, "name")

    #     df = df.query("duration >= 9.9")

    #     if self.sleepDF is not None:
    #         self.appendSleepStagesToEventDF(df)
    #         self.appendOffsetSleepStageToEventDF(df, -10)
    #         self.appendOffsetSleepStageToEventDF(df, -15)

    #     if self.positionDF is not None:
    #         self.appendBodyPositionsToEventDF(df)

    #     # remove all wake apneas/hypopneas, so all is relative to TST
    #     # df.drop(df.index[df.sleepStage == "W"], inplace=True)

    #     # tst = self.getMetaData("tst")

    #     # minimal duration 10 sec and not completly in Wake - AASM <- not alice compatible
    #     # minDuration = 8.5
    #     # maxDuration = 305

    #     # restrictionQuery = "duration > %f and duration < %f" % (minDuration, maxDuration)
    #     restrictionQuery = "duration > 0"
    #     obstructive = df.query('name == "obstructive"').query(restrictionQuery)
    #     mixed = df.query('name == "mixed"').query(restrictionQuery)
    #     central = df.query('name == "central"').query(restrictionQuery)
    #     hypopnea = df.query('name == "hypopnea"').query(restrictionQuery)
    #     apnea = df.query("name in ['obstructive', 'mixed', 'central']").query(restrictionQuery)
    #     apneaHypopnea = df.query("name in ['obstructive', 'mixed', 'central', 'hypopnea']").query(restrictionQuery)

    #     self.apneaDF = apnea
    #     self.apneaHypopneaDF = apneaHypopnea

    #     o = len(obstructive)
    #     m = len(mixed)
    #     c = len(central)
    #     h = len(hypopnea)

    #     a = o + m + c
    #     ah = a + h

    #     assert apnea["name"].count() == a
    #     assert apneaHypopnea["name"].count() == ah

    #     self.registerMetadata("countApneaObstructive", o, unit="#")
    #     self.registerMetadata("countApneaMixed", m, unit="#")
    #     self.registerMetadata("countApneaCentral", c, unit="#")  # 350

    #     self.registerMetadata("countHypopnea", h, unit="#")
    #     self.registerMetadata("countApneaHyponea", o + m + c + h, unit="#")

    #     self.registerMetadata("indexApnea", self.getIndexForEventCount(a), unit="#/h")
    #     self.registerMetadata("indexHypopnea", self.getIndexForEventCount(h), unit="#/h")
    #     self.registerMetadata("ahi", self.getIndexForEventCount(ah), unit="#/h")

    #     if ah > 0:
    #         self.registerMetadata("percentageApneaCentral", c / ah * 100, unit="%")
    #     else:
    #         self.registerMetadata("percentageApneaCentral", float("nan"), unit="%")

    #     self.registerMetadata("rdi", self.getIndexForEventCount(ah + self.getMetaData("countRera", 0)), unit="#")

    #     if self.positionDF is not None:
    #         apneaSupine = apnea[apnea.position.str.contains("Supine")]
    #         hypopneaSupine = hypopnea[hypopnea.position.str.contains("Supine")]
    #         ahSupine = apneaHypopnea[apneaHypopnea.position.str.contains("Supine")]
    #         ahOther = apneaHypopnea[apneaHypopnea.position.str.contains("Supine").eq(False)]

    #         durationSupine = self.getMetaData("positionSupineSleep", 0)
    #         durationOther = (
    #             self.getMetaData("positionLeft") + self.getMetaData("positionRight") + self.getMetaData("positionProne")
    #         )
    #         # self.registerMetadata("indexApneaBack", self.getIndexForEventCount(len(apneaSupine)), unit="#/h")
    #         # self.registerMetadata("indexHypopneaBack", self.getIndexForEventCount(len(hypopneaSupine)), unit="#/h")

    #         rdBack = len(ahSupine) + self.getMetaData("countReraBack", 0)

    #         rdNoBack = len(ahOther) + self.getMetaData("reraNoBack", 0)

    #         rdiNoRuckenIndex = rdNoBack / durationOther if rdNoBack else 0
    #         self.registerMetadata("rdiNoBack", rdiNoRuckenIndex * 60 * 60, unit="#/h")  # check 8143+8185+8196

    #         if durationSupine == 0:
    #             self.registerMetadata("ahiBack", 0, unit="#/h")
    #             self.registerMetadata("ahiNoBack", 0, unit="#/h")
    #             self.registerMetadata("rdiBack", 0, unit="#/h")
    #             self.registerMetadata("ratioRdiBack", 0, unit="#/h")
    #             self.registerMetadata("ratioAhiBack", 0, unit="#/h")
    #         else:
    #             self.registerMetadata("ahiBack", (len(ahSupine) / durationSupine) * 60 * 60, unit="#/h")
    #             self.registerMetadata("ahiNoBack", (len(ahOther) / durationOther) * 60 * 60, unit="#/h")
    #             rdiRuckenIndex = rdBack / durationSupine
    #             rdiBack = rdiRuckenIndex * 60 * 60
    #             self.registerMetadata("rdiBack", rdiRuckenIndex * 60 * 60, unit="#/h")
    #             rdiBackNoBack = rdiNoRuckenIndex * 60 * 60

    #             self.registerMetadata("ratioAhiBack", self.getMetaData("ahiBack") / self.getMetaData("ahiNoBack"), unit="")
    #             self.registerMetadata("ratioRdiBack", rdiBack / rdiBackNoBack if rdiBackNoBack > 0 else 0, unit="#/h")

    #     if self.sleepDF is not None:
    #         ahRem = apneaHypopnea.query("sleepStage == 'R'")
    #         ahNRem = apneaHypopnea.query("sleepStage in ['N1', 'N2', 'N3']")
    #         durationRem = self.getMetaData("r")
    #         durationNRem = self.getMetaData("nr")

    #         ahiRem = len(ahRem) / durationRem * 60 * 60 if durationRem > 0 else 0
    #         ahiNRem = len(ahNRem) / durationNRem * 60 * 60 if durationNRem > 0 else 0

    #         self.registerMetadata("ahiRem", ahiRem, unit="#/h")
    #         self.registerMetadata("ahiNrem", ahiNRem, unit="#/h")

    #         self.registerMetadata("ratioAhiRem", ahiRem / ahiNRem if ahiNRem > 0 else 0, unit="")

    #         rdNRem = len(ahNRem) + self.getMetaData("reraNRem", 0)
    #         rdiNRem = rdNRem / durationNRem if durationNRem > 0 else 0
    #         rdRem = len(ahRem) + self.getMetaData("reraRem", 0)
    #         rdiRem = rdRem / durationRem if durationRem > 0 else 0

    #         self.registerMetadata("rdiNrem", rdiNRem * 60 * 60, unit="#/h")
    #         self.registerMetadata("rdiRem", rdiRem * 60 * 60, unit="#/h")
    #         self.registerMetadata("ratioRdiRem", rdiRem / rdiNRem if rdiNRem > 0 else 0, unit="#/h")

    # def parseSpO2Events(self, ra: RecordAnnotation):
    #     df = self.getDataFrameForRecordAnnotation(ra, "name")

    #     if self.positionDF is not None:
    #         self.appendBodyPositionsToEventDF(df)

    #     if self.sleepDF is not None:
    #         self.appendSleepStagesToEventDF(df)

    #     timeLower90 = self.filterWake(df.query('name == "spo2_Lower90"')).duration.sum()
    #     tib = self.getMetaData("tib")
    #     tst = self.getMetaData("tst")
    #     nr = self.getMetaData("nr")
    #     r = self.getMetaData("r")

    #     percentageSpO2Lower90 = timeLower90 / tib * 100
    #     self.registerMetadata("percentageSpO2Lower90", percentageSpO2Lower90, unit="%")

    #     timeLower80 = self.filterWake(df.query('name == "spo2_Lower80"')).duration.sum()
    #     percentageSpO2Lower80 = timeLower80 / tib * 100
    #     self.registerMetadata("percentageSpO2Lower80", percentageSpO2Lower80, unit="%")

    #     minSpO2 = self.filterWake(df.query('name == "spo2_minPerEpoch"')).amplitude.min()
    #     self.registerMetadata("minSpO2", minSpO2, unit="%")

    #     meanSpO2 = self.filterWake(df.query('name == "spo2_meanPerEpoch"')).amplitude.mean()
    #     self.registerMetadata("meanSpO2", meanSpO2, unit="%")

    #     meanSpO2Rem = self.filterRemTrue(df.query('name == "spo2_meanPerEpoch"')).amplitude.mean()
    #     self.registerMetadata("meanSpO2Rem", meanSpO2Rem, unit="%")

    #     minSpO2Nrem = self.filterNremTrue(df.query('name == "spo2_meanPerEpoch"')).amplitude.mean()
    #     self.registerMetadata("meanSpO2Nrem", minSpO2Nrem, unit="%")

    #     countOxyDesat = len(df.query('name == "spo2_desaturation"'))
    #     self.registerMetadata("countOxyDesat", countOxyDesat, unit="#")

    #     indexOxyDesatNrem = len(self.filterNremTrue(df.query('name == "spo2_desaturation"'))) / (nr / 60 / 60)
    #     self.registerMetadata("indexOxyDesatNrem", indexOxyDesatNrem, unit="#/h")

    #     indexOxyDesatRem = len(self.filterRemTrue(df.query('name == "spo2_desaturation"'))) / (r / 60 / 60)
    #     self.registerMetadata("indexOxyDesatRem", indexOxyDesatRem, unit="#/h")

    #     indexOxyDesatTotal = countOxyDesat / (tst / 60 / 60)
    #     self.registerMetadata("indexOxyDesatTotal", indexOxyDesatTotal, unit="#/h")

    # def parseArousals(self, ra: RecordAnnotation):
    #     df = self.getDataFrameForRecordAnnotation(ra, "name")
    #     em = PSGEventManager()

    #     if self.checkMinDuration:
    #         df = df.query("duration >= 2.9")

    #     if self.sleepDF is not None:
    #         em.appendDataframe(df, self.sleepDF, colMap={"sleepStage-15": "name"}, offsetStart=-15, fixedDuration=15)
    #         df = self.filterWake(df, "sleepStage-15")
    #         self.appendSleepStagesToEventDF(df)
    #         tst = self.getMetaData("tst")

    #     rera = df.query("name == 'RERA' or name == 'arousal_rera'")
    #     arousal = df.query("name == 'Arousal' or name == 'arousal'")

    #     tst = self.getMetaData("tst")

    #     self.registerMetadata("countRera", len(rera), unit="#")
    #     self.registerMetadata("countArousal", len(arousal) + len(rera), unit="#")
    #     # self.registerMetadata("countArousal10", len(arousal.query("duration >= 3")), unit="#")

    #     if self.positionDF is not None and len(rera) > 0:
    #         self.appendBodyPositionsToEventDF(rera)
    #         reraBack = rera.query("position == 'Supine'")
    #         self.registerMetadata("countReraBack", len(reraBack), unit="#")
    #         self.registerMetadata("reraNoBack", len(rera) - len(reraBack), unit="#")

    #     if tst is not None:
    #         self.registerMetadata("indexRera", len(rera) / tst * 60, unit="#/h")
    #         self.registerMetadata("indexArousal", (len(arousal) + len(rera)) / tst * 60, unit="#/h")

    #         if self.sleepDF is not None:
    #             self.registerMetadata("reraRem", len(rera.query("sleepStage.str.contains('R')")), unit="#")
    #             self.registerMetadata("reraNRem", len(rera.query("sleepStage.str.contains('R').eq(False)")), unit="#")

    #     self.arousalDF = df

    # def parseSummary(self, ra: RecordAnnotation):
    #     pass
    #     # 1. Findings related to sleep diagnoses RECOMMENDED
    #     # 2. EEG abnormalities RECOMMENDED
    #     # 3. ECG abnormalities RECOMMENDED
    #     # 4. Behavioral observations RECOMMENDED
    #     # 5. Sleep hypnogram OPTIONAL

    # def parseCardiacEvents(self, ra: RecordAnnotation):
    #     pass
    #     # 1. Average heart rate during sleep RECOMMENDED
    #     # 2. Highest heart rate during sleep RECOMMENDED
    #     # 3. Highest heart rate during recording RECOMMENDED
    #     # 4. Occurrence of bradycardia (if observed); report lowest heart rate RECOMMENDED
    #     # 5. Occurrence of asystole (if observed); report longest pause RECOMMENDED
    #     # 6. Occurrence of sinus tachycardia during sleep (if observed); report highest heart rate RECOMMENDED
    #     # 7. Occurrence of narrow complex tachycardia (if observed); report highest heart rate RECOMMENDED
    #     # 8. Occurrence of wide complex tachycardia (if observed); report highest heart rate RECOMMENDED
    #     # 9. Occurrence of atrial fibrillation (if observed); report average heart rate RECOMMENDED
    #     # 10. Occurrence of other arrhythmias (if observed); list arrhythmia RECOMMENDED

    #     df = self.getDataFrameForRecordAnnotation(ra, "name")

    #     if self.positionDF is not None:
    #         self.appendBodyPositionsToEventDF(df)

    #     if self.sleepDF is not None:
    #         self.appendSleepStagesToEventDF(df)

    #     minHrSleep = self.filterWake(df.query('name == "hr_minPerEpoch"')).amplitude.min()
    #     self.registerMetadata("minHrSleep", minHrSleep, unit="%")

    #     maxHrSleep = self.filterWake(df.query('name == "hr_maxPerEpoch"')).amplitude.max()
    #     self.registerMetadata("maxHrSleep", maxHrSleep, unit="%")

    #     meanHrSleep = self.filterWake(df.query('name == "hr_meanPerEpoch"')).amplitude.mean()
    #     self.registerMetadata("meanHrSleep", meanHrSleep, unit="%")
    #     pass

    # def parseSleepStageEvents(self, ra: RecordAnnotation):
    #     df = self.getDataFrameForRecordAnnotation(ra, "name")
    #     if len(ra.events) == 0:
    #         return
    #     lastEvent = ra.events[len(ra.events) - 1]
    #     spt = lastEvent.start + lastEvent.duration

    #     wake = df[df.name == "W"]
    #     sleep = df[df.name != "W"]
    #     nrem1 = df[df.name == "N1"]
    #     nrem2 = df[df.name == "N2"]
    #     nrem3 = df[df.name == "N3"]
    #     rem = df[df.name == "R"]
    #     wakeTime = wake.sum()["duration"]
    #     nrem1Time = nrem1.sum()["duration"]
    #     nrem2Time = nrem2.sum()["duration"]
    #     nrem3Time = nrem3.sum()["duration"]
    #     remTime = rem.sum()["duration"]

    #     firstSleep = sleep.iloc[0]["start"]
    #     lastSleep = sleep.iloc[-1]["start"] + sleep.iloc[-1]["duration"]

    #     recordSeconds = self.record.dataCount
    #     sleepPeriod = df.query("start >= %f and start < %f" % (firstSleep, lastSleep))

    #     lightOn = recordSeconds if self.record.lightOn is None else self.record.lightOn

    #     tib = lightOn - self.record.lightOff

    #     tib = wakeTime + nrem1Time + nrem2Time + nrem3Time + remTime
    #     tst = nrem1Time + nrem2Time + nrem3Time + remTime

    #     # SPT = Sleep Period Time = TRT - Total recording time
    #     spt = lastSleep - firstSleep

    #     assert spt == sleepPeriod["duration"].sum(), "sleep events might overlap or have gaps"

    #     self.registerMetadata("w", wakeTime)
    #     self.registerMetadata("n1", nrem1Time)
    #     self.registerMetadata("n2", nrem2Time)
    #     self.registerMetadata("n3", nrem3Time)
    #     self.registerMetadata("r", remTime)
    #     self.registerMetadata("nr", nrem1Time + nrem2Time + nrem3Time)

    #     sleepOnset = sleep.iloc[0]["start"] if len(sleep) > 0 else None
    #     wSPT = sleepPeriod.query("name == 'W'")["duration"].sum()

    #     if sleepOnset is not None:

    #         # REPORT CONTENT
    #         # Schlafstadien:
    #         # l_off # oder: self.registerMetadata("lightsOut")  # hh:mm
    #         # l_on  # oder: self.registerMetadata("lightsOn")  # hh:mm
    #         self.registerMetadata("tst", tst)
    #         # trt
    #         self.registerMetadata("tib", tib)  # time in bed
    #         self.registerMetadata("spt", spt)
    #         self.registerMetadata("sLatency", sleepOnset)
    #         self.registerMetadata("rLatency", rem.iloc[0]["start"] - sleepOnset)
    #         self.registerMetadata("waso", spt - tst)
    #         self.registerMetadata("sEfficiency", tst / tib * 100, unit="%")
    #         self.registerMetadata("percentageW", wakeTime / tib * 100, unit="%")
    #         self.registerMetadata("percentageN1", nrem1Time / tst * 100, unit="%")
    #         self.registerMetadata("percentageN2", nrem2Time / tst * 100, unit="%")
    #         self.registerMetadata("percentageN3", nrem3Time / tst * 100, unit="%")
    #         self.registerMetadata("percentageR", remTime / tst * 100, unit="%")

    #         # NONE REPORT CONTENT
    #         self.registerMetadata("latencyN1", nrem1.iloc[0]["start"] - sleepOnset if len(nrem1) > 0 else None)
    #         self.registerMetadata("latencyN2", nrem2.iloc[0]["start"] - sleepOnset if len(nrem2) > 0 else None)
    #         self.registerMetadata("latencyN3", nrem3.iloc[0]["start"] - sleepOnset if len(nrem3) > 0 else None)
    #         self.registerMetadata("wSPT", wSPT, unit="s")

    #     self.sleepDF = df
