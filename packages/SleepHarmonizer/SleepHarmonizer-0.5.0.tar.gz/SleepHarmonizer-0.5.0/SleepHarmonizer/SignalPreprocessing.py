import numpy as np
from pyPhases import Swappable
from pyPhasesRecordloader import RecordSignal, Signal
from pyPhasesRecordloader import SignalPreprocessing as pyPhaseSignalPreprocessing
from scipy.signal import fftconvolve, firwin, iirfilter, kaiserord, lfilter, butter, filtfilt, iirnotch, resample_poly
from scipy.interpolate import interp1d


class SignalPreprocessing(pyPhaseSignalPreprocessing, Swappable):

    def _zerophase(self, b, a, x):
        y = lfilter(b, a, x)
        y = np.flip(y)
        y = lfilter(b, a, y)
        y = np.flip(y)
        return y

    def iir(self, signal: Signal, recordSignal: RecordSignal, order, lowcut, highcut, zerophase=True):
        b, a = iirfilter(order, [lowcut, highcut], btype="bandpass", ftype="butter", fs=signal.frequency, analog=False)

        if zerophase:
            y = self._zerophase(b, a, signal.signal)
        else:
            y = lfilter(b, a, signal.signal)

        signal.signal = y

    def fftConvolution(self, signal: Signal, recordSignal: RecordSignal, kernselSeconds):
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
            self.logError("shhs position only supports 0, 1, 2, 3 as values, conflicts: %s \n... fix in SignalPreprocessing.py" % checkValues)

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
            raise Exception("domino position only supports 0, 1, 2, 3, 4 as values ... fix in SignalPreprocessing.py")

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
            raise Exception("domino position only supports 1, 2, 3, 4, 5, 6 as values ... fix in SignalPreprocessing.py")

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
            raise Exception("alice position only supports 0, 3, 6, 9, 12 as values ... fix in SignalPreprocessing.py")

        signal.signal[signal.signal == 0] = 1
        signal.signal[signal.signal == 3] = 5
        signal.signal[signal.signal == 6] = 2
        signal.signal[signal.signal == 9] = 4
        signal.signal[signal.signal == 12] = 3

    def firEEG(self, signal: Signal, recordSignal: RecordSignal):
        self.iir(signal, recordSignal, 5, 0.5, 35, zerophase=True)

    def firEMG(self, signal: Signal, recordSignal: RecordSignal):
        self.iir(signal, recordSignal, 5, 0.5, 50, zerophase=True)
