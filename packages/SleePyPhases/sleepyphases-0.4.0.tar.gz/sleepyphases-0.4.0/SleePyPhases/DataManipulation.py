from random import shuffle
import numpy as np
from numpy.random import default_rng
from pyPhasesML import DataManipulation as pyPhasesDataManipulation
from pyPhases import Swappable


class DataManipulation(pyPhasesDataManipulation, Swappable):
    """
    X: (numSegments, numSamples, numChannels)
    Y: (numSegments, ... )
    """

    def __init__(self, steps, splitName, projectconfig, seed=2, threshold=None, recordMetadata=None, **kwargs) -> None:
        super().__init__(steps, splitName, **kwargs)
        self.catMatrix = None
        self.numLabels = projectconfig["numLabels"] if "numLabels" in projectconfig else 1
        self.numClasses = projectconfig["numClasses"] if "numLabels" in projectconfig else [1]
        self.rng = default_rng(seed=2)
        self.threshold = threshold
        self.recordMetadata = recordMetadata
        self.config = projectconfig

    def hotEncode(self, X, Y):
        Y = Y.astype(np.int32)
        shape = list(Y.shape)
        encodeVars = self.numLabels
        if self.numLabels == 1:
            encodeVars = self.numClasses[0]

        if self.catMatrix is None:
            self.catMatrix = np.eye(encodeVars)
            # append a zero line on the end so that -1 will map to all zeros
            self.catMatrix = np.concatenate((self.catMatrix, np.eye(1, encodeVars, -1))).astype(np.int32)
        Y = self.catMatrix[Y].reshape((shape[0], shape[1], encodeVars))
        return X, Y

    def hotEncodeMultiLabel(self, X, Y, classBins=None):
        classBins = classBins or self.numClasses
        Y = Y.astype(np.int32)
        shape = list(Y.shape)

        if self.catMatrix is None:
            self.catMatrix = []
            for classCount in classBins:
                self.catMatrix.append(np.concatenate((np.eye(classCount), np.eye(1, classCount, -1))).astype(np.int32))
        newY = [self.catMatrix[index][Y[:, :, index]].reshape((shape[0], shape[1], classCount)) for index, classCount in enumerate(classBins)]
        Y = np.concatenate(newY, axis=2)
        return X, Y

    def hotDecode(self, X, Y):
        Ynew = np.argmax(Y, axis=2)
        Ynew[Y.sum(axis=2) == 0] = -1
        return X, Ynew.reshape(Y.shape[0], Y.shape[1], 1)

    def znorm(self, X, Y):
        X = (X - X.mean(axis=1, keepdims=True)) / (X.std(axis=1, keepdims=True) + 0.000000001)
        return X, Y

    def MagScale(self, X, Y, low=0.8, high=1.25):
        scale = low + self.rng.random(1, dtype=X.dtype) * (high - low)
        X = scale * X

        return X, Y

    def channelShuffle(self, X, Y, channelSlice):
        channelSlice = slice(channelSlice[0], channelSlice[1])

        cutChannels = X[:, :, channelSlice].copy()
        self.rng.shuffle(cutChannels, axis=2)
        X[:, :, channelSlice] = cutChannels

        return X, Y

    def _fixeSizeSingleChannel(self, X, size, fillValue=0, position="center", startAt=0, moduloStart=1):
        newShape = list(X.shape)
        newShape[1] = size

        centerNew = size // 2
        signalSize = X.shape[1]
        centerSignal = signalSize // 2

        if startAt == 0 and position == "center":
            startAt = centerNew - centerSignal

        newX = np.full(newShape, fillValue, dtype=X.dtype)

        startAt -= startAt % moduloStart
        if startAt < 0:
            offsetStart = startAt * -1
            length = min(newShape[1], X.shape[1] - offsetStart)
            newX[:, :length, :] = X[:, offsetStart : offsetStart + newShape[1], :]
        else:
            newLength = min(startAt + signalSize, size)
            newX[:, startAt : startAt + signalSize, :] = X[:,0:newLength,:]

        return newX, startAt

    def reduceYOnly(self, X, Y, factor):
        return X, Y[:, ::factor, :]
    
    def reduceX(self, X, Y, factor, reduce="mean", channel=0):

        X[:, :, channel] = X.reshape((X.shape[0], X.shape[1] // factor, factor, 1))
        
        if reduce == "mean":
            X = X.mean(axis=2)
        elif reduce == "max":
            X = X.max(axis=2)

        return X, Y
    
    def _add_bool_padding(self, array, padding):

        padded = np.copy(array)
        for i in range(1, padding + 1):
            padded |= np.roll(array, i, axis=1)
            padded |= np.roll(array, -i, axis=1)
        return padded
    
    def physionetLabels(self, X, Y):
        # [Sleep, Arousal, Apnea]

        # ignore wake and apnea events
        sleep = Y[:, :, 0] <= 0
        apnea = Y[:, :, 2] > 0

        sleep = self._add_bool_padding(sleep, 10)
        apnea = self._add_bool_padding(apnea, 10)

        Y[sleep, 1] = -1
        Y[apnea, 1] = -1

        return X, Y
    
    def fixedSize(self, X, Y, size, fillValue=0, fillValueY=-1, position="center", moduloStart=1):
        X, startAt = self._fixeSizeSingleChannel(X, size, fillValue, position, moduloStart=moduloStart)
        Y, _ = self._fixeSizeSingleChannel(Y, size, fillValueY, position, startAt, moduloStart=moduloStart)
        return X, Y

    def fixedSizeX(self, X, Y, size, fillValue=0, position="center", moduloStart=1):
        X, _ = self._fixeSizeSingleChannel(X, size, fillValue, position, moduloStart=moduloStart)
        return X, Y

    def fixedSizeY(self, X, Y, size, fillValue=0, position="center", moduloStart=1):
        Y, _ = self._fixeSizeSingleChannel(Y, size, fillValue, position, moduloStart=moduloStart)
        return X, Y

    def restoreLength(self, X, Y, length):
        curLength = Y.shape[1]
        padLeft = (curLength - length) // 2

        return X, Y[:, padLeft : (padLeft + length), :]

    def selectChannel(self, X, Y, channel):
        return X[:, :, channel : channel + 1], Y

    def selectChannels(self, X, Y, channels):
        return X[:, :, channels], Y

    def selectChannelRandom(self, X, Y, channels):
        channel = self.rng.choice(channels)
        # keep selected channel and all other channels not listed
        return X[:, :, [i for i in range(X.shape[2]) if i == channel or i not in channels]], Y

    def changeType(self, X, Y, dtype, changeX=True, changeY=True):
        if changeX:
            X = X.astype(dtype)
        if changeY:
            Y = Y.astype(dtype)

        return X, Y
    
    def fitToReduction(self, X, Y, factor):
        if X.shape[1] % factor != 0:
            cutOff = X.shape[1] % factor
            print(
                f"data not divisible by factor {factor}, cutting {cutOff} samples, might be because recording does not fit entirely in the window 2^^21"
            )
            X = X[:, :-cutOff, :]
            Y = Y[:, :-cutOff, :]

        return X, Y

    def reduceY(self, X, Y, factor, reduce="mean"):
        """reduce prediction by factor and using the mean of the prediction, using majority for Y"""
        
        X, Y = self.fitToReduction(X, Y, factor)
        X = X.reshape((X.shape[0], X.shape[1] // factor, factor, X.shape[2]))
        Y = Y.reshape(Y.shape[0], Y.shape[1] // factor, factor, Y.shape[2])

        if reduce == "mean":
            X = X.mean(axis=2)
            arr = Y.astype(np.int32) if isinstance(Y, np.ndarray) else Y.int()
            Y = np.apply_along_axis(lambda x: np.bincount(x).argmax(), axis=2, arr=arr)
        elif reduce == "max":
            X = X.max(axis=2)
            Y = Y.max(axis=2)

        return X, Y

    def deleteIgnored(self, X, Y):
        """reduce prediction by factor and using the mean of the prediction, using majority for Y"""
        mask = Y[:, :, -1] != -1

        return X[mask].reshape(1, -1, X.shape[2]), Y[mask].reshape(1, -1, Y.shape[2])
    
    def deleteIgnoredLabelClassBin(self, X, Y):
        """reduce prediction by factor and using the mean of the prediction, using majority for Y"""
        numLabels = X.shape[2]
        yShape = Y.shape
        xShape = X.shape

        X = X.reshape(-1, numLabels)
        Y = Y.reshape(-1, numLabels)
        deleteIgnored = np.all(Y != -1, axis=1)
        X = X[deleteIgnored]
        Y = Y[deleteIgnored]

        return X.reshape(1, -1, xShape[2]), Y.reshape(1, -1, yShape[2])

    def deleteIgnoredMultiClass(self, X, Y, numClasses=None):
        """reduce prediction by factor and using the mean of the prediction, using majority for Y"""
        numClasses = numClasses or X.shape[2]
        yShape = Y.shape
        xShape = X.shape

        X = X.reshape(-1, numClasses)
        if Y.shape[2] == 1:
            Y = Y.reshape(-1)
            deleteIgnored = Y != -1
        else:
            Y = Y.reshape(-1, numClasses)
            s = Y.sum(axis=1)
            deleteIgnored = s != 0
        X = X[deleteIgnored]
        Y = Y[deleteIgnored]

        return X.reshape(xShape[0], -1, xShape[2]), Y.reshape(yShape[0], -1, yShape[2])

    def _reduction(self, Y, strategy="majority", options=None, ignoreZero=True):
        if strategy == "majority":
            bincounts = np.bincount(Y.astype(np.int32))
            return bincounts[1:].argmax() + 1 if ignoreZero else bincounts.argmax()
        elif strategy == "prefer":
            # check if options values exist
            for o in options:
                if o in Y:
                    return o
        else:
            raise ValueError(f"unknown strategy {strategy}")

    def _combineWithPatience(self, Y, patience=10, reduction="majority", reductionOptions=None):
        """reduce prediction by factor and using the mean of the prediction, using majority (of values > 0) for Y or a list of prefered values"""
        pos = np.where(Y == 0)[0]
        if len(pos) == 0:
            return Y

        lengths = np.diff(pos)
        lengths = np.append(lengths, len(Y) - pos[-1])
        lastEventStart = 0
        gap = 0
        for index, (position, length) in enumerate(zip(pos, lengths)):
            isEvent = length > 1
            if isEvent:
                # fill gaps with mode of previous and next event
                if gap > 0 and gap < patience:
                    nextEventEnd = pos[index + 1] if index + 1 < len(pos) else len(Y)
                    value = self._reduction(Y[lastEventStart:nextEventEnd], reduction, reductionOptions)
                    Y[lastEventStart:nextEventEnd] = value
                else:
                    # smooth last event
                    start = position + 1
                    end = position + length
                    value = self._reduction(Y[start:end], reduction, reductionOptions)
                    Y[start:end] = value
                lastEventStart = position + 1
                gap = 1
            else:
                gap += 1
        return Y

    def _minLength(self, Y, minLength=10):
        # Find all event chains
        pos = np.where(np.diff(Y) != 0)[0] + 1
        if len(pos) > 0:
            chains = np.split(Y, pos)
            # Replace chains shorter than min_length with 0s
            for i in range(len(chains)):
                if len(chains[i]) < minLength and chains[i][0] != 0:
                    start = pos[i - 1] if i > 0 else 0
                    end = start + len(chains[i])
                    Y[start:end] = 0
        return Y
    
    def _maxLength(self, Y, maxLength=10):
        # Find all event chains
        pos = np.where(np.diff(Y) != 0)[0] + 1
        if len(pos) > 0:
            chains = np.split(Y, pos)
            # Replace chains shorter than min_length with 0s
            for i in range(len(chains)):
                if len(chains[i]) > maxLength and chains[i][0] != 0:
                    start = pos[i - 1] if i > 0 else 0
                    end = start + len(chains[i])
                    Y[start:end] = 0
        return Y

    def _reduceMultiEvent(self, Y, reduction="majority", reductionOption=None):
        changes = np.where(np.diff(Y) != 0)[0] + 1
        event_boundaries = np.split(Y, changes)
        position = 0
        events = []
        for segment in event_boundaries:
            events.append((segment[0], position, len(segment)))
            position += len(segment)

        lastEvent = [0, 0]
        mergeLastEvents = -1
        for classIndex, position, length in events:
            if lastEvent[0] > 0 and classIndex > 0:
                if mergeLastEvents == -1:
                    mergeLastEvents = lastEvent[1]
            elif mergeLastEvents >= 0:
                Y[mergeLastEvents:position] = self._reduction(Y[mergeLastEvents:position], reduction, reductionOption)
                mergeLastEvents = -1
            lastEvent = (classIndex, position)

        return Y

    def toEventMultiLabelBin(
        self,
        X,
        Y,
        patience=10,
        minLength=3,
        maxLength=0,
        yIndex=0,
        frequency=50,
        recution="majority",
        reductionOption=None,
        nonePenalty=None,
        reduceMultiEvent=False,
    ):
        threshold = self.threshold[yIndex] if isinstance(self.threshold, list) else self.threshold
        patience = int(patience * frequency)
        minLength = int(minLength * frequency)

        X = np.where(X >= threshold, 1, 0)

        channelPrediction = X[:, :, yIndex].reshape(-1)
        channelPrediction = self._combineWithPatience(channelPrediction, patience, recution, reductionOption)

        if reduceMultiEvent:
            channelPrediction = self._reduceMultiEvent(channelPrediction, recution, reductionOption)

        if minLength > 0:
            channelPrediction = self._minLength(channelPrediction, minLength)

        if maxLength > 0:
            channelPrediction = self._maxLength(channelPrediction, maxLength)

        X[:, :, yIndex] = channelPrediction
        return X, Y
    
    def toEvent(
        self,
        X,
        Y,
        patience=10,
        minLength=3,
        maxLength=0,
        yIndex=0,
        frequency=50,
        recution="majority",
        reductionOption=None,
        nonePenalty=None,
        reduceMultiEvent=False,
    ):
        threshold = self.threshold[yIndex] if isinstance(self.threshold, list) else self.threshold
        patience = int(patience * frequency)
        minLength = int(minLength * frequency)

        xShape = X.shape
        if xShape[2] > 1:
            if nonePenalty == "threshold":
                nonePenalty = self.threshold
                X[:, :, 0] *= nonePenalty
            X = X.argmax(axis=2)
        else:
            X[X >= threshold] = 1
            X[X < threshold] = 0

        channelPrediction = X[:, :, yIndex].reshape(-1)
        channelPrediction = self._combineWithPatience(channelPrediction, patience, recution, reductionOption)

        if reduceMultiEvent:
            channelPrediction = self._reduceMultiEvent(channelPrediction, recution, reductionOption)

        if minLength > 0:
            channelPrediction = self._minLength(channelPrediction, minLength)

        if maxLength > 0:
            channelPrediction = self._maxLength(channelPrediction, maxLength)

        X[:, :, yIndex] = channelPrediction
        return X, Y
    
    def _toEpoch(self, X, epochSize=30, frequency=1, reduce="mean", cIndex=0):
        epochSize = int(epochSize * frequency)

        X = [X[:, :, index] for index in range(X.shape[2])]
        
        X[cIndex] = X[cIndex].reshape(X[cIndex].shape[0], -1, epochSize)

        def mode_with_bincount(row):
            counts = np.bincount(row)
            return np.argmax(counts)
        
        if reduce == "mean":
            X[cIndex] = X[cIndex].mean(axis=2)
        elif reduce == "max":
            X[cIndex] = X[cIndex].max(axis=2)
        elif reduce == "majority":
            major_values = np.apply_along_axis(mode_with_bincount, 1, X[cIndex][0].astype(np.int32))
            X[cIndex] = major_values.reshape(1, -1)
        return X
    
    def toEpoch(self, X, Y, epochSize=30, frequency=1, cIndex=0, reduceX="mean", reduceY="majority"):

        if reduceX is not None:
            X = self._toEpoch(X, epochSize=epochSize, frequency=frequency, reduce=reduceX, cIndex=cIndex)
        if reduceY:
            Y = self._toEpoch(Y, epochSize=epochSize, frequency=frequency, reduce=reduceY, cIndex=cIndex)

        return X, Y

    def toArousal(self, X, Y, patience=10, minLength=3, frequency=50):
        return self.toEvent(X, Y, patience=patience, minLength=minLength, frequency=frequency)

    def toApnea(self, X, Y, patience=10, minLength=10, frequency=50):
        return self.toEvent(X, Y, patience=patience, minLength=minLength, frequency=frequency)

    def derive(self, X, Y, channels):
        newChan = X[:, :, channels[0]] - X[:, :, channels[1]]
        X = np.concatenate((X, newChan[:, :, np.newaxis]), axis=2)
        return X, Y

    def selectChannelBestMetadata(self, X, Y, channels, metadataFields):
        metadata = self.recordMetadata[self.currentIndex]
        metadata = [metadata[k] for k in metadataFields]
        bestIndex = np.argmax(metadata)
        return X[:, :, [i for i in range(X.shape[2]) if i == bestIndex or i not in channels]], Y

    def selectYChannels(self, X, Y, channels):
        return X, Y[:, :, channels]

    def reduceYToBinary(self, X, Y, ychannel=0):
        ignoreIndex = Y[:, :, ychannel] == -1
        Y[:, :, ychannel] = (Y[:, :, ychannel] > 0).astype(np.int32)
        Y[ignoreIndex] = -1
        return X, Y

    def mapY(self, X, Y, ychannel, mapping={}):
        Y[:, :, ychannel] = np.vectorize(lambda x: mapping[x])(Y[:, :, ychannel])
        return X, Y

    def transposeX(self, X, Y, transpose=None):
        transpose = transpose or (0, 2, 1)
        return X.transpose(transpose), Y
    
    def transposeY(self, X, Y, transpose=None):
        return X, Y.transpose((0, 2, 1))
    
    def reshapeX(self, X, Y, reshape):
        return X.reshape(X.shape[0], *reshape), Y

    def reshapeY(self, X, Y, reshape):
        return X, Y.reshape(X.shape[0], *reshape)
    
    def epochArray(self, X, Y, sfreq, rfreq, scaler_flag=False):
        import mne
        info = mne.create_info(sfreq=sfreq, ch_types='eeg', ch_names=['Fp1'])
        
        # X = np.expand_dims(X, axis=1)
        X = X.transpose(0, 2, 1)
        if scaler_flag:
            scaler = mne.decoding.Scaler(info=info, scalings='median')
            X = scaler.fit_transform(X)
        X = mne.EpochsArray(X, info=info)
        X = X.resample(rfreq)
        X = X.get_data()
        
        return X, Y
    
    
    def _paddingSegments(self, array, paddingSize):
        """adds a zero filled segments before and after the array

        Args:
            paddingSize ([int]): padding size in samples
        """
        _, windowSize, numChannels = array.shape
        padding = np.zeros((paddingSize, windowSize, numChannels))

        return np.concatenate((padding, array, padding))
    
    def _temporalContext(self, X, contextSize):
        _, windowSize, numChannels = X.shape
        size = len(X)

        marginSize = contextSize // 2
        paddedX = self._paddingSegments(X, marginSize)

        newX = np.empty((size, contextSize, windowSize, numChannels), dtype=X.dtype)

        for XId in range(marginSize, size + marginSize):
            startAt = XId - marginSize
            endWith = XId + marginSize + 1
            newX[startAt:, ::, ::, ::] = paddedX[startAt:endWith, ::, ::]
            # assert all(newX[startAt, ::, 10] == array[startAt, ::, 0])

        return newX

    def temporalContext(self, X, Y, contextSize):
        return self._temporalContext(X, contextSize), self._temporalContext(Y, contextSize)
    
    def shuffle(self, X, Y):
        indices = np.arange(X.shape[0])
        shuffle(indices)
        return X[indices], Y[indices]
        
    def stackTensors(self, X, Y):
        import torch
        X = torch.stack([torch.tensor(x) for x in X]).reshape(-1, *X[0].shape[1:])
        Y = torch.stack([torch.tensor(y) for y in Y]).reshape(-1, *Y[0].shape[1:])
        return X, Y
    
    def to_cuda(self, X, Y):
        return X.cuda(), Y.cuda()
    
    def to_tensor(self, X, Y, dtypex='float32', dtypey='float32'):
        import torch
        dtype_map = {
            "float32": torch.float32,
            "float64": torch.float64,
            "float16": torch.float16,
            "int32": torch.int32,
            "int64": torch.int64,
            "int16": torch.int16,
            "int8": torch.int8,
            "uint8": torch.uint8,
            "bool": torch.bool,
            "long": torch.long,
        }

        if isinstance(X, list):
            X = X.stack()

        return torch.tensor(X, dtype=dtype_map[dtypex]), torch.tensor(Y, dtype=dtype_map[dtypey])
    
    def to_numpy(self, X, Y):
        if not isinstance(X, np.ndarray):
            X = X.detach().cpu().numpy()
        if not isinstance(Y, np.ndarray):
            Y = Y.detach().cpu().numpy()
        return X, Y
    
    def clip_and_scale(self, X, Y, min_value, max_value):
        return X.clamp(min=min_value, max=max_value) / max([abs(min_value), abs(max_value)]), Y
    
    def batchNumpy(self, X, Y):

        return np.array(X), np.array(Y)

    def torch_spectrogram(self, signal, n_fft=None, hop=None, window=np.hanning):
        import torch

        window = window(n_fft) / window(n_fft).sum()
        window = torch.from_numpy(window).to(signal.device).float()
        stft = torch.stft(
            signal,
            n_fft=n_fft,
            hop_length=hop,
            win_length=n_fft,
            window=window,
            onesided=True,
            center=False,
            normalized=False,
            return_complex = True
        )
        stft = torch.view_as_real(stft)
        stft = (stft ** 2).sum(-1)
        return stft
    
    def spectogram(self, X, Y, fs, window_duration=2, window_overlap=1, logpower=True, clamp=1e-20):
        import torch

        fs = fs
        ws, hop = 2 ** int(np.log2(fs * window_duration) + 1), fs * window_overlap
        batch_size, temporal_context, n_channels, signal_length = X.shape
        X = X.view(batch_size * temporal_context, n_channels, signal_length).reshape(-1, signal_length)
        X = self.torch_spectrogram(X, hop=hop, n_fft=ws).float()
        X = torch.clamp(X, clamp, 1e32)
        if logpower:
            X = torch.log10(X)
        frequency_features, spectro_length = X.shape[1], X.shape[2]
        X = X.view(batch_size, temporal_context, n_channels, frequency_features, spectro_length)
        return X, Y

    def standardize_online(self, X, Y, axis, eps=1e-15):
        
        def multi_std(x, axis, unbiased=True):
            base_shape = list(x.shape)
            for ax in axis:
                x = x.unsqueeze(-1)
                x = x.transpose(ax, -1)
                base_shape[ax] = 1
            new_shape = tuple(base_shape + [-1])
            x = x.contiguous().view(new_shape)
            return x.std(-1, unbiased=unbiased)


        def multi_mean(x, axis):
            for ax in axis:
                x = x.mean(ax, keepdim=True)
            return x
        
        mu = multi_mean(X, axis)
        sigma = multi_std(X, axis)
        return (X - mu) / (sigma + eps), Y

    def toSegments(self, X, Y, segmentLength, segmentLengthLabel):
        X = X.reshape(-1, segmentLength, X.shape[-1])
        Y = Y.reshape(-1, segmentLengthLabel, Y.shape[-1])

        return X, Y
    
    def temporal_context(self, X, Y, epochSize, position="center"):
        #    Batch, Length, Channels -> Batch, TemporalContext, Length, Channels
        batch_size, length, channels = X.shape
        
        padding_size = epochSize // 2
        
        # Create zero-padded array
        padding = np.zeros((padding_size, length, channels))
        padded_X = np.concatenate((padding, X, padding))
        
        # Initialize output array
        output_X = np.zeros((batch_size, epochSize, length, channels))
        
        # Fill temporal context windows
        for i in range(batch_size):
            start_idx = i
            end_idx = start_idx + epochSize
            output_X[i] = padded_X[start_idx:end_idx]
        
        return output_X, Y
    def temporal_context_left(self, X, Y, contextSize):
        #    Batch, Length, Channels -> Batch, TemporalContext, Length, Channels

        # batch_size, length, channels = X.shape
        # batch_size, length, channels = X.shape
        batch_size = X.shape[0]
        others = X.shape[1:]
        
        # We can only start after we have enough context
        valid_segments = batch_size - (contextSize - 1)
        
        # Initialize output arrays for valid segments
        output_X = np.zeros((valid_segments, contextSize, *others))
        output_Y = Y[contextSize-1:]
        
        # Fill temporal context windows using only previous segments
        for i in range(valid_segments):
            start_idx = i
            end_idx = start_idx + contextSize
            output_X[i] = X[start_idx:end_idx]
        
        return output_X, output_Y
    
    def batch(self, X, Y, batchSize):
        # X = X.reshape(-1, batch_size, X.shape[-1])
        # Y = Y.reshape(-1, batch_size, Y.shape[-1])
        # X = X.reshape(-1, batch_size, X.shape[-1])
        # Y = Y.reshape(-1, batch_size, Y.shape[-1])
        return X, Y

        
    def spectrogram_sleeptransformer(self, X, Y, fs, epoch_second, win_size, overlap):
        
        import torch
        import torch.fft
        
        # Convert input to tensor if not already
        if not isinstance(X, torch.Tensor):
            X = torch.from_numpy(X).float()
        if not isinstance(Y, torch.Tensor):
            Y = torch.from_numpy(Y)
        
        # Calculate NFFT
        nfft = int(2**torch.ceil(torch.log2(torch.tensor(win_size*fs))))
        
        segments, length, channels = X.shape
        spec_len = nfft//2
        
        # Initialize output tensor
        spectrograms = torch.zeros((segments, epoch_second-1, spec_len, channels))
        
        nperseg = int(win_size*fs)
        noverlap = int(overlap*fs)
        step = nperseg - noverlap
        
        # Create Hamming window
        window = torch.hamming_window(nperseg).to(X.device)
        
        X_reshaped = X.reshape(-1, length)  # (segments*channels, length)
        
        # Create segments for all channels at once
        indices = torch.arange(0, length-nperseg+1, step)
        segments_data = torch.stack([X_reshaped[:, i:i+nperseg] for i in indices])  # (time_steps, segments*channels, nperseg)
        
        # Apply window to all segments simultaneously
        segments_data = segments_data * window.unsqueeze(0).unsqueeze(0)
        
        # Compute FFT for all segments at once
        fft_data = torch.fft.rfft(segments_data, n=nfft-1)
        
        # Compute magnitude
        magnitude = torch.abs(fft_data)  # (time_steps, segments*channels, freq_bins)
        
        # Reshape back to original dimensions
        spectrograms = magnitude.permute(1, 0, 2).reshape(segments, channels, -1, magnitude.shape[-1])
        spectrograms = spectrograms.permute(0, 2, 3, 1)  # (segments, time_steps, freq_bins, channels)
        
        return spectrograms, Y

    def toDefaultEventWindows(X, Y, window_size=10, iou_threshold=0.5, windowCount=208):
        """
        Generate a label signal from binary signals representing arousals, leg movements, and apnea-hypopnea.
        
        Parameters:
        - binary_signals: numpy array of shape (T, 3) with binary signals for arousals, leg movements, and apnea-hypopnea.
        - window_size: size of the default event window in samples.
        - iou_threshold: Intersection-over-Union threshold for non-maximum suppression.
        
        Returns:
        - label_signal: numpy array of shape (T,) with event labels.
        """
        signalLength = Y.shape[0]
        
        # evently distribute eventwindows
        eventStarts = np.linspace(0, signalLength, windowCount, endpoint=False, dtype=int)
        trueEventStart = np.where(Y[:, 0] == 1)[0]

        # Assign event labels (e.g., 1 for arousal, 2 for leg movement, 3 for apnea-hypopnea)
        label_signal = np.zeros(signalLength, dtype=int)
        # Create default event windows and assign labels based on overlap
        for i in range(3):  # Iterate over the three event types
            event_windows = []
            for t in range(signalLength):
                if Y[t, i] == 1:
                    start = max(0, t - window_size // 2)
                    end = min(signalLength, t + window_size // 2)
                    event_windows.append((start, end, event_labels[i]))
            
            # Apply non-maximum suppression based on IoU threshold
            suppressed_windows = []
            while event_windows:
                best_window = max(event_windows, key=lambda x: x[1] - x[0])
                event_windows.remove(best_window)
                suppressed_windows.append(best_window)
                event_windows = [
                    (start, end, label) for (start, end, label) in event_windows
                    if (min(best_window[1], end) - max(best_window[0], start)) / (end - start) <= iou_threshold
                ]
            
            # Assign labels to the label signal
            for start, end, label in suppressed_windows:
                label_signal[start:end] = label
        
        return label_signal
    
    def toYOLOStyleLabels(self, X, Y, grid_size=16384):
        batchSize, signal_length, num_classes = Y.shape
        cell_size = signal_length // grid_size

        # Initialize the label tensor
        labels = np.zeros((batchSize, grid_size, 4 + num_classes))

        for b in range(batchSize):
            for i in range(num_classes):
                event_starts = np.where(np.diff(Y[b, :, i]) == 1)[0]
                event_ends = np.where(np.diff(Y[b, :, i]) == -1)[0]
                
                for start, end in zip(event_starts, event_ends):
                    event_center = (start + end) // 2
                    event_width = end - start
                    
                    grid_cell = event_center // cell_size
                    
                    if grid_cell < grid_size:
                        cell_start = grid_cell * cell_size
                        cell_end = (grid_cell + 1) * cell_size
                        
                        # Calculate IOU
                        intersection = min(end, cell_end) - max(start, cell_start)
                        union = max(end, cell_end) - min(start, cell_start)
                        iou = intersection / union if union > 0 else 0

                        labels[b, grid_cell, 0] = (event_center % cell_size) / cell_size  # x offset
                        labels[b, grid_cell, 1] = event_width / signal_length  # width
                        labels[b, grid_cell, 2] = iou  # confidence (IOU)
                        labels[b, grid_cell, 3 + i] = 1  # class

        return X, labels
    
    def checkNaN(self, X, Y):
        if np.isnan(X).any():
            raise ValueError("NaN values found in X.")
        if np.isnan(Y).any():
            raise ValueError("NaN values found in Y.")
        return X, Y
    
    def spectogram(self, X, Y, fs, epoch_second, win_size, overlap):
        import numpy as np
        
        # transform to segments (sleep epoches)
        segmentLength = epoch_second * fs
        X = X.reshape(-1, segmentLength)
        segments, _ = X.shape

        # Calculate FFT size as next power of 2 above win_size*fs
        nfft = int(2**np.ceil(np.log2(win_size*fs)))
        spec_len = nfft//2
        
        # Calculate window parameters
        nperseg = int(win_size*fs)
        noverlap = int(overlap*fs)
        step = nperseg - noverlap
        
        # Create Hamming window
        window = np.hamming(nperseg)
        
        # Initialize output array
        num_windows = len(range(0, segmentLength-nperseg+1, step))
        spectrograms = np.zeros((segments, num_windows, spec_len))
        
        # Process each segment
        for seg in range(segments):
            data = X[seg, :]
            indices = np.arange(0, segmentLength-nperseg+1, step)
            segments_data = np.array([data[i:i+nperseg] for i in indices])
        segments_data = segments_data * window
        fft_data = np.fft.rfft(segments_data, n=nfft-1)
        spectrograms[seg] = np.abs(fft_data)
        
        return spectrograms
    
    def extendEvents(self, X, Y, channel=0, pre_samples=0, post_samples=0):
        # Get the target channel
        y_channel = Y[:, :, channel].copy()
        y_channel[Y[:, :, channel] == -1] = 0
        
        # Find event boundaries (1s)
        event_starts = np.where(np.diff(y_channel, prepend=0) == 1)[1]
        event_ends = np.where(np.diff(y_channel, append=0) == -1)[1]
        
        # Extend each event
        for start, end in zip(event_starts, event_ends):
            # Calculate extended boundaries
            new_start = max(0, start - pre_samples)
            new_end = min(y_channel.shape[1], end + 1 + post_samples)
            
            # Fill the extended region with 1s
            y_channel[:, new_start:new_end] = 1

        y_channel[Y[:, :, channel] == -1] = -1
        
        # Update the channel in Y
        Y[:, :, channel] = y_channel
        
        return X, Y
    
    
    def combineY(self, X, Y, values, channel=0):
        """" Combine multiple Y values into one. """
        smallest = min(values)
        Y[:, :, channel] = np.where(np.isin(Y[:, :, channel], values), values[-1], Y[:, :, channel])
        Y[:, :, channel][Y[:, :, channel] > smallest] -= len(values) - 1
        
        return X, Y