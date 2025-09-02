from typing import List

from pyPhasesML import FeatureExtraction as pyPhasesFeatureExtraction
from pyPhasesRecordloader import RecordSignal, Signal, Event, ChannelsNotPresent
from pyPhases import Swappable

class PreManipulation(Swappable):

    def step(self, stepname: str, recordSignal: RecordSignal, events: List[Event], name=None, **options) -> Signal:
        if hasattr(self, stepname):
            # call method
            return getattr(self, stepname)(recordSignal, events, **options)
        else:
            raise Exception(f"PreManipulation '{stepname}' not found")

    def __init__(self, config) -> None:
        self.config = config

    def __call__(self, recordSignal, events):
        config = self.config.copy()
        for c in config:
            name = c["name"]
            ret = self.step(name, recordSignal, events, **c)
            if ret is not  None:
                recordSignal, events = ret
        return recordSignal, events

    def discard_records_not_all_sleepstages(self, recordSignal: RecordSignal, events: List[Event]):
        sleepEventNames = ["R", "N1", "N2", "N3"]
        allSleepStages = ["W"] + sleepEventNames

        allSleepEvents = [e.name for e in events if e.name in allSleepStages]

        if set(allSleepEvents) != set(allSleepStages):
            raise ChannelsNotPresent("AllSleepStages")

        return recordSignal, events
    
    def keepSignals(self, recordSignal, events: List[Event], channels):
        recordSignal = recordSignal[channels]

        return recordSignal, events
        
    def _trimEventsByOffset(self, events, startOffset, endOffset):        
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
        return newEvents
    
    def _trimEventByRemoveOffset(self, events: List[Event], removeStart: int, removeEnd: int):        
        newEvents = []

        diffDuration = removeEnd - removeStart
        for event in events:
            eventEnd = event.end()

            if eventEnd <= removeStart:
                newEvents.append(event)
                continue
            if event.start > removeEnd:
                event.start -= diffDuration
                newEvents.append(event)
                continue

            # event is bigger than the cutted portion
            if event.start < removeStart and eventEnd > removeEnd:
                event.duration -= diffDuration
                if event.duration > 0:
                    newEvents.append(event)
            # event starts before cutting
            elif event.start < removeStart:
                event.duration -= removeStart - event.start
                if event.duration > 0:
                    newEvents.append(event)
            # event starts in the middle of the cut
            elif event.start > removeStart:
                event.duration -= removeEnd - event.start
                event.start = removeStart
                if event.duration > 0:
                    newEvents.append(event)

            # else the cutting is inside the cutting (or excatly the same) remove it

        return newEvents
    
    def _removeEvents(self, events: List[Event], removeEvents: List[Event]):
        startOffset = 0 
        for remEvent in removeEvents:
            events = self._trimEventByRemoveOffset(events, remEvent.start-startOffset, remEvent.end()-startOffset)
            startOffset += remEvent.duration
        return events

        
    def remove_undefined(self, recordSignal: RecordSignal, events: List[Event]):
        import numpy as np
        
        undefinedStages = [e for e in events if e.name == "undefined"]

        # expect all signals to same shape
        keepSignal = np.ones(recordSignal.getSignalLength(), dtype=bool)
        fs = recordSignal.targetFrequency

        for event in undefinedStages:
            start = int(event.start * fs)
            end = int(event.end() * fs)
            keepSignal[start:end] = False

        recordSignal.signalCutBySignalBoolSignal(keepSignal)

        removeEvents = [e for e in events if e.name == "undefined"]

        events = self._removeEvents(events, removeEvents)
        events = [e for e in events if e.name != "undefined"]

        return recordSignal, events
    
    
    def balance_wake(self, recordSignal: RecordSignal, events: List[Event]):
        allSleepStages = ["R", "N1", "N2", "N3", "W"]
        sleepStageDuration = {s: 0 for s in allSleepStages}

        for e in events:
            if e.name in allSleepStages:
                sleepStageDuration[e.name] += e.duration

        # Sort items by duration in descending order
        sleepStageDuration = sorted(sleepStageDuration.items(), key=lambda x: x[1], reverse=True)        
        
        if sleepStageDuration[0][0] == "W":
            import numpy as np
            diff = sleepStageDuration[0][1] - sleepStageDuration[1][1]
            signalLength = recordSignal.signals[0].signal.shape[0]
            fs = recordSignal.targetFrequency

            sleepEvents = [e for e in events if e.name in allSleepStages]
            eveningW = sleepEvents[0].end() if sleepEvents[0].name == "W" else 0
            morningW = sleepEvents[-1].duration if sleepEvents[-1].name == "W" else 0


            if eveningW > diff:
                startOffset = diff
                endOffset = int(signalLength / fs)
            else:
                startOffset = eveningW
                keepMorningW = max(0, eveningW + morningW - diff)
                endOffset = sleepEvents[-1].start + keepMorningW

            events = self._trimEventsByOffset(events, startOffset, endOffset)
            recordSignal.signalOffset(startOffset, endOffset, offsetFrequency=1)

        return recordSignal, events
    
    
    def trimSPT(self, recordSignal: RecordSignal, events: List[Event], before, after):
        allSleepStages = ["R", "N1", "N2", "N3", "W"]
        sleepEvents = [e for e in events if e.name in allSleepStages]

        # length = int(recordSignal.getSignalLength() / recordSignal.targetFrequency)
        
        offsetStart = sleepEvents[0].end()-before if sleepEvents[0].name == "W" else 0
        offsetEnd = sleepEvents[-1].start+ after if sleepEvents[-1].name == "W" else sleepEvents[-1].end()

        offsetStart = max(offsetStart, 0)
        offsetEnd = min(offsetEnd, sleepEvents[-1].end())

        recordSignal.signalOffset(offsetStart, offsetEnd, offsetFrequency=1)
        events = self._trimEventsByOffset(events, offsetStart, offsetEnd)

        return recordSignal, events
    
    def trimToLightAndScoring(self, recordSignal: RecordSignal, events: List[Event], addOffset = None, fillLastSleepstage=False):
        addOffset = addOffset or [0, 0]
        # add wake to relevant stages to cut only undefined
        allSleepStages = ["R", "N1", "N2", "N3", "W"]
        sleepEventNames = allSleepStages
        offsetStart = None
        offsetEnd = None

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
        
        recordSignal.signalOffset(startOffset, endOffset, offsetFrequency=1)
        events = self._trimEventsByOffset(events, startOffset, endOffset)

        return recordSignal, events