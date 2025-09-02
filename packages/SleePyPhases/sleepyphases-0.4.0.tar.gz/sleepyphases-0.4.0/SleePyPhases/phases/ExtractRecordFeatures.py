import numpy as np
from pyPhases import Phase
from pyPhasesRecordloader import ChannelsNotPresent, RecordLoader
from tqdm import tqdm


class ExtractRecordFeatures(Phase):
    """
    load record ids
    """

    def addEEGSignalQuality(self, signal):
        from scipy.stats import kurtosis, skew
        if signal.dimension in ["uV"]:
            pass
        elif signal.dimension in ["mV"]:
            signal.signal = signal.signal * 1000
        else:
            self.logError(f"Unkown Signaldimension '{str(signal.dimension)}' in signal '{signal.name}', assuming 'uV'")
        signal.bandpass(low=0.3, high=35, order=3)
        defaultWindowSize = 8
        if signal.signal.shape[0] % (defaultWindowSize * signal.frequency):
            signal.signal = signal.signal[
                : int(signal.signal.shape[0] / (defaultWindowSize * signal.frequency))
                * int(defaultWindowSize * signal.frequency)
            ]
        windowed = np.reshape(
            signal.signal,
            (round(len(signal.signal) / (defaultWindowSize * signal.frequency)), round(defaultWindowSize * signal.frequency)),
        )
        # Kriterien inkl. Schwelllwerten aus der Veröffentlichung DOI: 10.1109/JBHI.2019.2920381
        highAmpl = np.sum(abs(windowed) > 151.09, axis=1) / windowed.shape[1] > (
            1 / defaultWindowSize * 0.5
        )  # 95: 95, 100: 151.09
        highStd = np.std(windowed, axis=1) > 33.23  # 95: 22.29, 100: 33.23
        # highApEn = ... > 0.65 # 95: 1.01, 100: 0.65
        # highAmplVar = (np.max(abs(windowed), axis=1) / np.square(np.std(windowed, axis=1))) > 1.02e5 # 95: 1.56e5, 100: 1.02e5
        highKurt = kurtosis(windowed, axis=1, bias=False) > 14.56  # 95: 6.53, 100: 14.56
        highSkew = abs(skew(windowed, axis=1, bias=False)) > 1.79  # 95: 0.69, 100: 1.79

        sumArtefacts = highAmpl + highStd + highKurt + highSkew
        signal.quality = 1 - (sum(sumArtefacts) / len(sumArtefacts))

        return signal.quality

    def main(self):
        metaData = self.project.getData("metadata", list)
        rl = RecordLoader.get()
        for record in tqdm(metaData):
            recordId = record["recordId"]
            if "EEG F4-A1-quality" in record or not record["annotationExist"]:
                continue
            try:
                recordSignal = rl.getSignal(recordId)
            except ChannelsNotPresent:
                continue

            for channel in recordSignal.signals:
                if channel.typeStr == "eeg":
                    quality = self.addEEGSignalQuality(channel)
                    record[channel.name + "-quality"] = quality
        self.registerData("metadata", metaData)
