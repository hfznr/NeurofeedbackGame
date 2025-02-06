import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
import os  # Import os module to handle directories

class EMGProcessor:
    def __init__(self, sampling_frequency, lowcut, highcut):
        self.sampling_frequency = sampling_frequency
        self.lowcut = lowcut
        self.highcut = highcut

    def bandpass_filter(self, data):
        nyquist = 0.5 * self.sampling_frequency
        low = self.lowcut / nyquist
        high = self.highcut / nyquist
        b, a = butter(4, [low, high], btype='band')
        y = filtfilt(b, a, data)
        return y

    def notch_filter(self, data, notch_freq=50.0, quality_factor=30.0):
        nyquist = 0.5 * self.sampling_frequency
        notch = notch_freq / nyquist
        b, a = butter(2, [notch - notch / quality_factor, notch + notch / quality_factor], btype='bandstop')
        y = filtfilt(b, a, data)
        return y
