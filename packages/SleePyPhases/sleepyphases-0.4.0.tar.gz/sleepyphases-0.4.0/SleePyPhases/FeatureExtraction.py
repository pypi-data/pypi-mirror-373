import math
from typing import List

import numpy as np
from pyPhases import Swappable
from pyPhasesML import FeatureExtraction as pyPhasesFeatureExtraction
from pyPhasesML import ModelManager
from pyPhasesRecordloader import RecordSignal

from .DataManipulation import DataManipulation


class FeatureExtraction(pyPhasesFeatureExtraction, Swappable):
    """batchManipulation for the physionet challenge 2023
    segmentSignal: Recordsignal of the segment with 18 EEG channels
    """

    def __init__(self, project) -> None:
        super().__init__()
        self.project = project

    def time(self, segmentSignal: RecordSignal):
        segmentLength = segmentSignal.getShape()[1]
        # segmentLengthInHOurs = segmentLength / segmentSignal.targetFrequency / 3600
        # hour, minutes = segmentSignal.start.split(":")
        # startTimeInHours = int(hour) + int(minutes) / 60
        # endTimeInHours = startTimeInHours + segmentLengthInHOurs
        hour = segmentSignal.start
        endTimeInHours = hour + 1
        return np.linspace(hour, endTimeInHours, segmentLength)
    
    def epochIndex(self, segmentSignal: RecordSignal, windowSize, factor):
        _channels, length = segmentSignal.getShape()
        factor = windowSize * segmentSignal.targetFrequency
        windowCount = math.ceil(length / factor)
        arangeArray = np.arange(0, windowCount).astype(np.int16)
        featureSignalArray = np.repeat(arangeArray, factor)
        return featureSignalArray[:length]
    
    def epochCyclic(self, segmentSignal: RecordSignal, cycleLength):
        _channels, signalLength = segmentSignal.getShape()
        factor = cycleLength * segmentSignal.targetFrequency
        windowCount = math.ceil(signalLength / factor)

        arangeArray = np.arange(0, factor).astype(np.int16)
        # featureSignalArray = [np.cos(np.pi * arangeArray / length)]
        # featureSignalArray = np.repeat(featureSignalArray, factor)[:length]
        cosArray = np.cos(2 * np.pi * arangeArray / factor)
        
        # Repeat the cosine array to cover the entire signal length
        featureSignalArray = np.tile(cosArray, windowCount)[:signalLength]

        return featureSignalArray

    def featureModel(self, segmentSignal: RecordSignal, featureName: str, xChannels: List[str]):
        import torch
        useGPU = torch.cuda.is_available() and False
        with self.project:
            config = self.project.config["featureConfigs", featureName]
            self.project.config.update(config)
            self.project.addConfig(config)

            self.project.trigger("configChanged", None)
            self.project.setConfig("trainingParameter.batchSize", 1)
            self.project.setConfig("recordWise", True)

            modelPath = self.project.getConfig("featureModel", torch)

            # this is needed for mutlithreading
            ModelManager.loadModel(self.project)
            # get feature model
            model = ModelManager.getModel(True)
            model.useGPU = useGPU
            state = model.load(modelPath)
            model.loadState(state)
            featureModel = model.model.eval()

            featureModel = featureModel.cuda() if useGPU else featureModel.cpu()

            # we assum that the segment is already preprocessed for the model
            array = segmentSignal.getSignalArray(xChannels, transpose=True)

            da = DataManipulation.getInstance(self.project.config["segmentManipulation"], self.project.getConfig("datasetSplit"), self.project.config, recordAnnotations={})
            array, _ = da((array, None))
            array = array.transpose(2, 1, 0)

            features = model.predict(array, get_likelihood=True, returnNumpy=True)
            _, features = da.restoreLength(None, features, length=segmentSignal.getShape()[1])
            features = features[:, :, 1]

        return features
        
    def toSegments(self, X, Y, segmentLength, segmentLengthLabel):
        X = X.reshape(-1, segmentLength, X.shape[-1])
        Y = Y.reshape(-1, segmentLengthLabel, Y.shape[-1])

        return X, Y

    def spectogram(self, recordSignal: RecordSignal, fs, epoch_second, win_size, overlap):
        import numpy as np
        
        # Calculate FFT size as next power of 2 above win_size*fs
        nfft = int(2**np.ceil(np.log2(win_size*fs)))
        
        # Get input dimensions
        segments, length, channels = X.shape
        spec_len = nfft//2
        
        # Calculate window parameters
        nperseg = int(win_size*fs)
        noverlap = int(overlap*fs)
        step = nperseg - noverlap
        
        # Create Hamming window
        window = np.hamming(nperseg)
        window = window / np.sum(window)
        
        # Initialize output array
        num_windows = len(range(0, length-nperseg+1, step))
        spectrograms = np.zeros((segments, channels, num_windows, spec_len))
        
        # Process each channel independently
        for ch in range(channels):
            X = recordSignal.getSignalByName(ch)
            for seg in range(segments):
                # Get data for current segment and channel
                data = X[seg, :, ch]
                
                # Create overlapping segments
                indices = np.arange(0, length-nperseg+1, step)
                segments_data = np.array([data[i:i+nperseg] for i in indices])
                
                # Apply window function
                segments_data = segments_data * window
                
                # Compute FFT
                fft_data = np.fft.rfft(segments_data, n=nfft-1)
                
                # Calculate magnitude spectrum
                spectrograms[seg, ch] = np.abs(fft_data)
        
        # Rearrange dimensions to match expected output format (segments, time, frequency, channels)
        spectrograms = np.transpose(spectrograms, (0, 2, 3, 1))
        
        return spectrograms
