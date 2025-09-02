import math
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from pyPhasesRecordloader import RecordSignal
from datetime import timedelta

from pyPhases.util.EventBus import EventBus


class Plot(EventBus):
    def __init__(self, reportFolder) -> None:
        self.reportFolder = reportFolder
        self.createLogFolder(self.reportFolder)
        
    def createLogFolder(self, path=None):
        path = path or self.reportFolder
        Path(path).mkdir(parents=True, exist_ok=True)
        Path(path).joinpath("examples").mkdir(parents=True, exist_ok=True)

    def plotClassDistribution(self, data: dict, name="", title="", plotHeader=True, sort=True, continuousX=False):
        if sort:
            data = dict(sorted(data.items(), key=lambda item: item[0]))

        classNames = data.keys()
        values = np.array(list(data.values()))
        plt.clf()
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.bar(classNames, values)
        plt.title(title)
        ges = values.sum()
        
        
        if continuousX:
            xtick_labels = [tick.get_text() for tick in ax.get_xticklabels()]
            adjusted_xtick_labels = []
            for i, label in enumerate(xtick_labels):
                if i % 2 == 1:
                    label = '\n' + label  # Add a newline character to shift even labels down
                adjusted_xtick_labels.append(label)
            ax.set_xticklabels(adjusted_xtick_labels)

        if plotHeader:
            for i in range(len(classNames)):
                plt.text(
                    i,
                    values[i],
                    "%i (%.2f%%)" % (values[i], values[i] / ges * 100),
                    ha="center",
                    bbox=dict(facecolor="orange", alpha=0.8),
                )

    def plotSignal(self, data: dict, name="", title="", plotHeader=True, sort=True):
        if sort:
            data = dict(sorted(data.items(), key=lambda item: item[0]))

        classNames = data.keys()
        values = np.array(list(data.values()))
        plt.clf()
        plt.bar(classNames, values)
        plt.title(title)
        ges = values.sum()

        if plotHeader:
            for i in range(len(classNames)):
                plt.text(
                    i,
                    values[i],
                    "%i (%.2f%%)" % (values[i], values[i] / ges * 100),
                    ha="center",
                    bbox=dict(facecolor="orange", alpha=0.8),
                )

        self.save(name)

    def save(self, name):
        # plt.savefig(f"{self.reportFolder}/{name}.svg")
        plt.savefig(f"{self.reportFolder}/{name}.png")
        plt.close()

    def plotRecordSignal(
        self,
        recordSignal: RecordSignal,
        signalSlice=None,
        title="Example from Signal {record} from {from} to {to}",
        resample=True,
        secondsPerInch=1,
        highlights=None,
        padding=0,
        sizeFactor=1,
        fig = None,
        axs = None
    ):
        # signalArray = recordSignal.getSignalArray(signalNames)
        # if signalNames is None:
        #     signalNames = recordSignal.signalNames[channelSlice]

        channelCount, recordSignalLength = recordSignal.getShape(forceRecalculate=True)
        if signalSlice is None:
            signalSlice = slice(0, recordSignalLength, 1)
        else:
            start, end = signalSlice
            # start = max(0, start - padding)
            # end = min(end + padding, recordSignalLength)
            signalSlice = slice(start, end, 1)

        # if figsize in [[32,32], None]:
        # figsize = figsize if figsize is not None else [32, 32]
        signalLength = signalSlice.stop - signalSlice.start
        frequency = recordSignal.targetFrequency

        # channels = signalArray.shape[1]
        # cm_to_inch = 1/2.54
        newFigsize = (math.ceil(signalLength / frequency / (secondsPerInch)), int(channelCount * 1 + 1))

        # newFigsize = (math.ceil(signalLength / frequency / (secondsPerInch) / 7), int(channelCount * 1 + 1))
        # newFigsize = newFigsize[0] * sizeFactor, newFigsize[1] * sizeFactor
        time = np.linspace(signalSlice.start / frequency, signalSlice.stop / frequency, signalLength)
        # time += signalSlice.start / frequency

        tplDict = {
            "record": recordSignal.recordId,
            "from": timedelta(seconds=time[0]),
            "to": timedelta(seconds=time[1]),
        }
        title = title.format(**tplDict)

        if fig is None:
            fig, axs = plt.subplots(channelCount, 1, sharex=True, figsize=newFigsize, squeeze=True)
        else:
            axs = axs

        # plotSignals =
        alpha = 0.3
        fig.subplots_adjust(hspace=0.2, wspace=5)
        if channelCount == 1:
            axs = [axs]
        axs[0].set_title(title)
        axs[-1].set_xlabel("Time (s)")

        # x_tick_labels = []
        # for x_tick in axs[i].get_xticks():
        #     dt = datetime.utcfromtimestamp(x_tick)
        #     x_tick_labels.append(dt.strftime("%H:%M:%S"))
        # axs[i].set_xticklabels(x_tick_labels)
        axs[-1].xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: str(timedelta(seconds=val))))

        axs[0].set_xlim([min(time), max(time)])

        for index, signal in enumerate(recordSignal.signals):
            self.trigger("beforePlotSignal", signal, axs, index)
            if resample:
                signal.resample(frequency)

            label = signal.name
            if bool(signal.dimension):
                label += f" ({signal.dimension})"

            axs[index].plot(time, signal.signal[signalSlice])
            axs[index].set_ylabel(signal.name)

            self.trigger("afterPlotSignal", signal, axs, index)

            if highlights is not None:
                for start, end in highlights:
                    if end < 0:
                        end += signalSlice.stop / frequency
                    else:
                        end += signalSlice.start / frequency
                    start += signalSlice.start / frequency
                    axs[index].axvspan(start, end, color="green", alpha=alpha)

        fig.tight_layout()
        return fig

    def plotArrays(
        self,
        arrays,
        labels,
        figSize=None,
        fig = None,
        axs = None,
    ):
        channelCount, recordSignalLength = len(arrays), len(arrays[0])

        if fig is None:
            fig, axs = plt.subplots(channelCount, 1, sharex=True, figsize=figSize, squeeze=True)
        else:
            axs = axs

        fig.subplots_adjust(hspace=0.2, wspace=5)
        if channelCount == 1:
            axs = [axs]

        for index, array in enumerate(arrays):
            label = labels[index]

            axs[index].plot(range(len(array)), array)
            axs[index].set_ylabel(label)

        return fig
