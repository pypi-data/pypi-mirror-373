
import pandas as pd
from pyPhases import Phase
from pyPhases.util import BatchProgress
from pyPhasesRecordloader import AnnotationNotFound, RecordLoader
import tqdm


class ExtractEvents(Phase):
    """
    Extract numpy arrays from the raw records in the dataset
    """

    useMultiThreading = True
    threads = None
    validatDataset = True

    def getEventList(self, recordId):
        rl = RecordLoader.get()
        try:
            return rl.getEventList(recordId)
        except AnnotationNotFound:
            return None


    def getEvents(self, records, force=False):
        rl = RecordLoader.get()
        
        bp = BatchProgress(records)
        bp.useMultiThreading = self.useMultiThreading
        if self.threads is not None:
            bp.threads = self.threads

        def combine(events, index):
            combine.events.append([e for e in events if e is not None])
        # def combineFlatten(events, index):
        #     combine.events += [e for ev in events if ev is not None for e in ev]
        # def getEventList(recordId):
        #     rl.getEventList(recordId)
        combine.events = []

        # bp.asyncQueue(rl.getEventList, records, combine)
        bp.start(self.getEventList, records, combine)
        return combine.events
    
    def appendDataframe(self, df, dfToAppend, colMap, offsetStart=None, offsetEnd=None):
        cols = {n: [] for n in colMap}
        if offsetStart is None:
            offsetStart = 0
        if offsetEnd is None:
            offsetEnd = 0
        for e in df.iloc:
            start = e.start + offsetStart
            end = e.end + offsetEnd
            possibleEvents = dfToAppend.query("start < %f and end > %f" % (end, start))
            for name in cols:
                cols[name].append(",".join([ev[colMap[name]] for ev in possibleEvents.iloc]))
        for name in cols:
            df[name] = cols[name]

    def generateData(self, name):
        if name == "events":
            groupedRecords = self.project.getData("allDBRecordIds", list)
            flatten = [r for records in groupedRecords.values() for r in records]
            # extract the data
            events = self.getEvents(flatten)
            self.registerData("events", events)
        if name == "eventDF":
            allRecordEventsBatches = self.getData("events", list)
            events = []
            recordIndex = 0
            for allRecordEvents in tqdm.tqdm(allRecordEventsBatches):
                for recordEvents in allRecordEvents:
                    for event in recordEvents:
                        events.append({
                            "recordIndex": recordIndex,
                            "name": event.name,
                            "start": event.start,
                            "duration": event.duration,
                        })
                    recordIndex += 1
            df = pd.DataFrame.from_dict(events)
            df["end"] = df["start"] + df["duration"]
            dfSleepStage = df.query("name in ['W', 'N1', 'N2', 'N3', 'R']")
            dfArousal = df.query("name in ('arousal', 'arousal_rera')")
            dfLM = df.query("name in ('LegMovement-Left', 'LegMovement-Right')")
            eventResp = df.query("name in ('resp_hypopnea', 'resp_centralapnea', 'resp_obstructiveapnea', 'resp_mixedapnea', 'resp_cheynestokesbreath')")

            self.registerData("eventArousal", dfArousal)
            self.registerData("eventLM", dfLM)
            self.registerData("eventSleep", dfSleepStage)
            self.registerData("eventResp", eventResp)

            self.appendDataframe(dfArousal, dfSleepStage, {"sleepStage": "name"}, offsetStart=-0.5, offsetEnd=0.5)
            self.appendDataframe(dfArousal, dfLM, {"legmovements": "name"}, offsetStart=-0.5, offsetEnd=0.5)
            self.appendDataframe(dfArousal, eventResp, {"resp_event": "name"}, offsetStart=-0.5, offsetEnd=0.5)

            self.registerData("eventDF", dfArousal)
            
            return dfArousal
    
    def appendDataframe(self, df, dfToAppend, colMap, offsetStart=None, offsetEnd=None, idQuery=""):
        cols = {n: [] for n in colMap}
        if offsetStart is None:
            offsetStart = 0
        if offsetEnd is None:
            offsetEnd = 0
        for e in tqdm.tqdm(df.iloc):
            start = e.start + offsetStart
            end = e.end + offsetEnd
            possibleEvents = dfToAppend.query("recordIndex == %i and start < %f and end > %f" % (e.recordIndex, end, start))
            for name in cols:
                cols[name].append(",".join([ev[colMap[name]] for ev in possibleEvents.iloc]))
        for name in cols:
            df[name] = cols[name]
            
    def plotArousalHist(self, df, col, name):
        from matplotlib import pyplot as plt
        
        df[col].plot(kind='hist', bins=100, density=False)
        plt.xlabel(name)
        # plt.ylabel('Density')
        plt.ylabel('Arousal Count')
        plt.title('Distribution of %s (M=%.2f, μ=%.2f, σ=%.2f)'%(name, df["duration"].median(), df["duration"].mean(), df["duration"].std()))



    def main(self):
        from matplotlib import pyplot as plt
        import matplotlib.ticker as ticker
        
        from SleePyPhases.Plot import Plot
        
        # df = self.getData("eventDF")
        df = self.getData("eventDF", list)
        
        modelConfigString = self.project.getDataFromName("eventDF").getTagString()
        logPath = f"eval/{modelConfigString}/"
        self.logPath = logPath
        plot = Plot(logPath)
        plot.createLogFolder()
        plot.plotClassDistribution(df.groupby("name")["recordIndex"].count(), "Arousal/Rera")
        plot.save("arousal-rera")
        plot.plotClassDistribution(df.query("name == 'arousal'").groupby("sleepStage")["recordIndex"].count(), "sleepStage Arousal")
        plot.save("arousal-sleepStage")
        plot.plotClassDistribution(df.query("name == 'arousal_rera'").groupby("sleepStage")["recordIndex"].count(), "sleepStage Rera")
        plot.save("rara-sleepStage")
        plot.plotClassDistribution(df.query("name == 'arousal_rera'").groupby("sleepStage")["recordIndex"].count(), "sleepStage")
        plot.save("sleepStage")
        
        df["type"] = df.apply(lambda row: ("L" if row["legmovements"] != "" else "") + ("R" if row["resp_event"] != "" else ""), axis=1)
        df["first_resp"] = df.apply(lambda row: row["resp_event"].split(",")[0], axis=1)
        
        plot.plotClassDistribution(df.groupby("type")["recordIndex"].count(), "type")
        plot.save("type")
        
        plot.plotClassDistribution(df.query("first_resp != ''").groupby("first_resp")["recordIndex"].count())
        plot.save("first_resp")
        
        
        plot.plotClassDistribution(df.groupby("resp_event")["recordIndex"].count(), "resp_events")
        plot.save("resp_events")
        
        
        # df["duration"].plot(kind='density')
        self.plotArousalHist(df, "duration", "Duration")
        plt.text(10 + 2.5, plt.ylim()[1]*0.9, "10", color='red', ha='center', va='bottom')
        plt.axvline(x=10, color='red')
        plot.save("duration")
        
        self.plotArousalHist(df.query("name == 'arousal_rera'"), "duration", "Rera Duration")
        plt.text(10 + 2.5, plt.ylim()[1]*0.9, "10", color='red', ha='center', va='bottom')
        plt.axvline(x=10, color='red')
        plot.save("rera-duration")
        
        self.plotArousalHist(df.query("name == 'arousal'"), "duration", "Arousal Duration")
        plt.text(10 + 2.5, plt.ylim()[1]*0.9, "10", color='red', ha='center', va='bottom')
        plt.axvline(x=10, color='red')
        plot.save("arousal-duration")
        
        self.plotArousalHist(df.query("name == 'arousal'"), "start", "Arousal Start")
        plot.save("arousal-start")
        
        self.plotArousalHist(df.query("name == 'arousal_rera'"), "start", "Rera Start")
        plot.save("rera-start")
        
        self.plotArousalHist(df, "start", "Start")
        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x/3600:.1f}h"))
        plot.save("start")
        
        
