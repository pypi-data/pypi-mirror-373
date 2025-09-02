import contextlib

import numpy as np
from pyPhases import Swappable
from pyPhasesRecordloader import ChannelsNotPresent, RecordSignal, Signal
from pyPhasesRecordloader import SignalPreprocessing as pyPhaseSignalPreprocessing


class SignalPreprocessing(pyPhaseSignalPreprocessing, Swappable):

    def rls(self, signal: Signal, recordSignal: RecordSignal, channels: list, resampleSteps: list):
        import padasip as pa
        
        remoeSignals = []
        for channel in channels:
            with contextlib.suppress(ChannelsNotPresent):
                s = recordSignal.getSignalByName(channel)
                [self.step(processStep, s, recordSignal) for processStep in resampleSteps]
                remoeSignals.append(s.signal)
        n = len(remoeSignals)
        if n > 0:
            remoeSignals = np.array(remoeSignals).transpose(1, 0)
            f = pa.filters.FilterRLS(n=n, mu=0.995, w="random")
            y, e, w = f.run(signal.signal, remoeSignals)
            if not np.isnan(np.sum(e)):
                signal.signal = e
            else:
                self.logError(f"RLS Error in: {recordSignal.recordId}")

    def _zerophase(self, b, a, x):
        from scipy.signal import lfilter
        
        y = lfilter(b, a, x)
        y = np.flip(y)
        y = lfilter(b, a, y)
        y = np.flip(y)
        return y

    def iir(self, signal: Signal, recordSignal: RecordSignal, order, lowcut, highcut, zerophase=True):
        from scipy.signal import iirfilter, lfilter
        
        b, a = iirfilter(order, [lowcut, highcut], btype="bandpass", ftype="butter", fs=signal.frequency, analog=False)

        if zerophase:
            y = self._zerophase(b, a, signal.signal)
        else:
            y = lfilter(b, a, signal.signal)

        signal.signal = y

    def fftConvolution(self, signal: Signal, recordSignal: RecordSignal, kernselSeconds):
        from scipy.signal import fftconvolve
        
        kernel_size = int(kernselSeconds * signal.frequency) + 1

        # Compute and remove moving average with FFT convolution
        resultShape = signal.signal.shape
        center = np.zeros(resultShape)

        center = fftconvolve(signal.signal, np.ones(shape=(kernel_size,)) / kernel_size, mode="same")

        signal.signal = signal.signal - center

        # Compute and remove the rms with FFT convolution of squared signal
        scale = np.ones(resultShape)

        temp = fftconvolve(np.square(signal.signal), np.ones(shape=(kernel_size,)) / kernel_size, mode="same")

        # Deal with negative values (mathematically, it should never be negative, but fft artifacts can cause this)
        temp[temp < 0] = 0.0

        # Deal with invalid values
        invalidIndices = np.isnan(temp) | np.isinf(temp)
        temp[invalidIndices] = 0.0
        maxTemp = np.max(temp)
        temp[invalidIndices] = maxTemp

        # Finish rms calculation
        scale = np.sqrt(temp)

        # To correct records that have a zero amplitude signal
        scale[(scale == 0) | np.isinf(scale) | np.isnan(scale)] = 1.0
        signal.signal = signal.signal / scale

    def fftConvolution18m(self, signal: Signal, recordSignal: RecordSignal):
        self.fftConvolution(signal, recordSignal, 18 * 60)

    def normalizePercentage70(self, signal: Signal, recordSignal: RecordSignal):
        self.cut(signal, recordSignal, 70, 100)
        self.normalize(signal, recordSignal, 0, 1)

    def getFilterCoefficients(self, signal, tansitionWidth=15.0, cutOffHz=30.0, rippleDB=40.0):
        from scipy.signal import firwin, kaiserord
        nyq_rate = signal.frequency / 2.0
        width = tansitionWidth / nyq_rate
        N, beta = kaiserord(rippleDB, width)
        if nyq_rate <= cutOffHz:
            cutOffHz = nyq_rate - 0.001
            self.logWarning("Cutoff frequency for FIR was adjusted to nyquist frequency.")

        # Use firwin with a Kaiser window to create a lowpass FIR filter.
        return firwin(N, cutOffHz / nyq_rate, window=("kaiser", beta))

    def antialiasingFIR(self, signal: Signal, recordSignal: RecordSignal):
        signal.signal = np.convolve(signal.signal, self.getFilterCoefficients(signal), mode="same")

    def resampleFIR(self, signal: Signal, recordSignal: RecordSignal, targetFrequency=None):
        targetFrequency = targetFrequency or recordSignal.targetFrequency
        if signal.frequency != targetFrequency:
            self.antialiasingFIR(signal, recordSignal)
            self.resample(signal, recordSignal, targetFrequency)

    def positionSHHS(self, signal: Signal, recordSignal: RecordSignal):
        uniquePositions = set(np.unique(signal.signal))
        # RIGHT, LEFT, BACK, FRONT (derived from the profusion xml, not sure if the mapping is actually correct)
        checkValues = set(uniquePositions) - {0, 1, 2, 3}
        if len(checkValues) > 0:
            # there are some records with invalid values (like shhs1-202947), we just set them to 0
            # shhs1-203716
            signal.signal[np.isin(signal.signal, list(checkValues))] = 0
            self.logError("shhs position only supports 0, 1, 2, 3 as values, conflicts: %s \n... fix here :-)" % checkValues)

        signal.signal += 10  # overwrite protection
        signal.signal[signal.signal == 10] = 5
        signal.signal[signal.signal == 11] = 3
        signal.signal[signal.signal == 12] = 2
        signal.signal[signal.signal == 13] = 4

    def positionMESA(self, signal: Signal, recordSignal: RecordSignal):
        # sourcery skip: raise-specific-error
        uniquePositions = set(np.unique(signal.signal))
        # Right, Back, Left, Front, Upright (derived from the profusion xml, not sure if the mapping is actually correct)
        checkValues = set(uniquePositions) - {0, 1, 2, 3, 4}
        if len(checkValues) > 0:
            raise Exception("mesa position only supports 0, 1, 2, 3, 4 as values ... fix here :-)")

        signal.signal += 10  # overwrite protection
        signal.signal[signal.signal == 10] = 5
        signal.signal[signal.signal == 11] = 2
        signal.signal[signal.signal == 12] = 3
        signal.signal[signal.signal == 13] = 4
        signal.signal[signal.signal == 14] = 1

    def positionDomino(self, signal: Signal, recordSignal: RecordSignal):
        # sourcery skip: raise-specific-error
        uniquePositions = set(np.unique(signal.signal))
        checkValues = set(uniquePositions) - {1, 2, 3, 4, 5, 6}
        if len(checkValues) > 0:
            raise Exception("domino position only supports 1, 2, 3, 4, 5, 6 as values ... fix here :-)")

        signal.signal[signal.signal == 1] = 4
        signal.signal[signal.signal == 2] = 1
        signal.signal[signal.signal == 3] = 3
        signal.signal[signal.signal == 4] = 5
        signal.signal[signal.signal == 5] = 1
        signal.signal[signal.signal == 6] = 2

    def positionAlice(self, signal: Signal, recordSignal: RecordSignal):
        # sourcery skip: raise-specific-error
        uniquePositions = set(np.unique(signal.signal))
        checkValues = set(uniquePositions) - {0, 3, 6, 9, 12}
        if len(checkValues) > 0:
            raise Exception("alice position only supports 0, 3, 6, 9, 12 as values ... fix here :-)")

        signal.signal[signal.signal == 0] = 1
        signal.signal[signal.signal == 3] = 5
        signal.signal[signal.signal == 6] = 2
        signal.signal[signal.signal == 9] = 4
        signal.signal[signal.signal == 12] = 3

    def firEEG(self, signal: Signal, recordSignal: RecordSignal):
        self.iir(signal, recordSignal, 5, 0.5, 35, zerophase=True)

    def firEMG(self, signal: Signal, recordSignal: RecordSignal):
        self.iir(signal, recordSignal, 5, 0.5, 50, zerophase=True)

    def butter_bandpass_filter(self, signal: Signal, recordSignal: RecordSignal, low_cut, high_cut, order=5):
        from scipy.signal import butter, lfilter

        nyq = 0.5 * signal.frequency
        if low_cut == 0:
            low_cut = 0.5
        low = low_cut / nyq
        high = high_cut / nyq
        b, a = butter(order, [low, high], btype="band")
        signal.signal = lfilter(b, a, signal.signal, axis=-1)

# def butter_bandpass_filter(self, signal: Signal, recordSignal: RecordSignal, low_cut=1.0, high_cut=50.0, order=5):
        from scipy.signal import butter, lfilter

        nyq = 0.5 * signal.frequency
        low = low_cut / nyq
        high = high_cut / nyq
        b, a = butter(order, [low, high], btype="band")
        
        # Apply the filter to the signal using lfilter
        signal.signal = lfilter(b, a, signal.signal)
    
    
    def poly_resample(self, signal: Signal, recordSignal: RecordSignal):
        # self.freq
        from scipy.signal import resample_poly
        
        signal_frequency = signal.frequency
        target_frequency = recordSignal.targetFrequency

        if signal_frequency != target_frequency:
            signal_duration = signal.signal.shape[0] / signal_frequency
            resampled_length = round(signal_duration * target_frequency)
            resampled_signal = resample_poly(signal.signal, target_frequency, signal_frequency, axis=0)
            if len(resampled_signal) < resampled_length:
                padding = np.zeros((resampled_length - len(resampled_signal), signal.signal.shape[-1]))
                resampled_signal = np.concatenate([resampled_signal, padding])
            signal.signal = resampled_signal
            signal.frequency = target_frequency

    def normalize_signal_IQR(self, signal: Signal, recordSignal: RecordSignal, clip_value=None, clip_IQR=None, eps=1e-5):
            
            if clip_value is not None:
                clipped_signal = np.clip(signal.signal, a_min=-clip_value, a_max=clip_value)
            elif clip_IQR is not None:
                s_low = np.percentile(signal.signal, 50, axis=0, keepdims=True) - np.percentile(
                    signal.signal, 25, axis=0, keepdims=True
                )
                s_high = np.percentile(signal.signal, 75, axis=0, keepdims=True) - np.percentile(
                    signal.signal, 50, axis=0, keepdims=True
                )
                clipped_signal = np.clip(signal.signal, a_min=-2 * clip_IQR * s_low, a_max=2 * clip_IQR * s_high)

            else:
                clipped_signal = signal.signal

            mu = np.median(clipped_signal, axis=0, keepdims=True)
            sigma = np.percentile(clipped_signal, 75, axis=0, keepdims=True) - np.percentile(
                clipped_signal, 25, axis=0, keepdims=True
            )
            sigma[sigma == 0] = eps
            signal.signal =  (clipped_signal - mu) / (sigma)
            
    def padding(self, signal: Signal, recordSignal: RecordSignal, duration, value=0):
        fs = signal.frequency
        padding_array = np.zeros(int(duration * fs)) + value
        signal = [padding_array] + [signal.signal] + [padding_array]
        return np.concatenate(signal)
       
    def fir(self, signal: Signal, recordSignal: RecordSignal, nFir, cutoff, pass_zero=False):
        from scipy import signal as scipySignal

        fs = signal.frequency
        nyq = fs/2

        band = [cutoff[0]/nyq, cutoff[1]/nyq] if isinstance(cutoff, list) else cutoff/nyq
        b = signal.firwin(nFir, band, pass_zero=pass_zero)
        signal.signal = signal.filtfilt(b, [1], signal.signal)