from spectrum_lib.spectrum_lib import SpectrumMath
from neuro_impl.utils import BB_channels
import os
import wfdb
import numpy as np
from datetime import datetime

class SpectrumController:
    def __init__(self):
        sampling_rate = 250
        fft_window = sampling_rate * 4
        process_win_rate = 5
        bord_frequency = 50
        normalize_spect_by_bandwidth = True
        delta_coef = 0.0
        theta_coef = 1.0
        alpha_coef = 1.0
        beta_coef = 1.0
        gamma_coef = 0.0

        self.maths = {BB_channels[i]: SpectrumMath(sampling_rate, fft_window, process_win_rate) for i in range(4)}
        for ch in BB_channels:
            self.maths[ch].init_params(bord_frequency, normalize_spect_by_bandwidth)
            self.maths[ch].set_waves_coeffs(delta_coef, theta_coef, alpha_coef, beta_coef, gamma_coef)

        self.processedSpectrum = None
        self.processedWaves = None

        self.saved_data_dir = "./wfdb_data"
        os.makedirs(self.saved_data_dir, exist_ok=True)

        # Raw signal and timestamp storage
        self.raw_signals = {ch: [] for ch in BB_channels}
        self.timestamps = []  # list of datetime objects
        self.labels = []
        self.current_label = 0
        self.is_recording = False

    def process_data(self, brain_bit_data):
        try:
            now = datetime.now()
            samples = brain_bit_data if isinstance(brain_bit_data, list) else [brain_bit_data]
            # extract values
            values = {ch: [] for ch in BB_channels}
            for pkt in samples:
                for ch in BB_channels:
                    values[ch].append(getattr(pkt, ch) * 1e3)
                # record timestamp for each pkt sample
                self.timestamps.append(now)

            if self.is_recording:
                for ch in BB_channels:
                    self.raw_signals[ch].extend(values[ch])
                self.labels.extend([self.current_label] * len(samples))

            # spectrum processing
            for ch in BB_channels:
                self.maths[ch].push_and_process_data(values[ch])
            self.__resolve_spectrum()
            self.__resolve_waves()
            for ch in BB_channels:
                self.maths[ch].set_new_sample_size()
        except Exception as e:
            print(f"Error processing data: {e}")

    def save_as_wfdb(self,path = "", name="eeg_recording"):
        """Save raw EEG channels, then timestamp as the last channel."""
        try:
            full_path = os.path.join(self.saved_data_dir, path)
            os.makedirs(full_path, exist_ok=True)  # Ensure directory exists
            if not self.timestamps:
                print("No data to save.")
                return
            # Reference start time
            t0 = self.timestamps[0]
            # Compute offsets in seconds
            time_offsets = [(t - t0).total_seconds() for t in self.timestamps]

            # Build signals array: [O1, O2, T3, T4, Time]
            channel_data = [self.raw_signals[ch] for ch in BB_channels]
            channel_data.append(time_offsets)
            signals = np.array(channel_data, dtype=np.float32).T

            # Units and names: channels first, then Time
            units   = ['mV'] * len(BB_channels) + ['s']
            names   = list(BB_channels)     + ['Time']
            fmts    = ['16'] * signals.shape[1]

            wfdb.wrsamp(
                record_name=name,
                fs=250,
                units=units,
                sig_name=names,
                p_signal=signals,
                fmt=fmts,
                write_dir=full_path,
            )
            print(f"Signals with timestamps saved to WFDB (Time last) at {full_path}")
        except Exception as e:
            print(f"Error saving WFDB signals: {e}")


    def save_as_wfdb_label(self,path = "", name="eeg_recording_label"):
        """Save labels then timestamps to WFDB record (Time last)."""
        try:
            full_path = os.path.join(self.saved_data_dir, path)
            os.makedirs(full_path, exist_ok=True)  # Ensure directory exists
            if not self.timestamps:
                print("No labels to save.")
                return
            t0 = self.timestamps[0]
            # Compute offsets in seconds
            time_offsets = [(t - t0).total_seconds() for t in self.timestamps]
            labels_arr = np.array(self.labels, dtype=np.float32)

            # Build signals array: [Frequency, Time]
            channels = [labels_arr, time_offsets]
            signals = np.array(channels, dtype=np.float32).T

            # Units and names: label first, then Time
            units   = ['Hz', 's']
            names   = ['Frequency', 'Time']
            fmts    = ['16',    '16']

            wfdb.wrsamp(
                record_name=name,
                fs=250,
                units=units,
                sig_name=names,
                p_signal=signals,
                fmt=fmts,
                write_dir=full_path,
            )
            print(f"Labels with timestamps saved to WFDB (Time last) at {full_path}")
        except Exception as e:
            print(f"Error saving WFDB labels: {e}")


    def update_labels(self, label):
        try:
            self.current_label = label
        except Exception as e:
            print(f"Error updating label: {e}")

    def start_recording(self):
        try:
            self.is_recording = True
            self.raw_signals = {ch: [] for ch in BB_channels}
            self.timestamps = []
            self.labels = []
            print("EEG recording started...")
        except Exception as e:
            print(f"Error starting recording: {e}")

    def stop_recording(self,path = ""):
        try:
            if self.is_recording:
                self.is_recording = False
                self.save_as_wfdb(path = path)
                self.save_as_wfdb_label(path=path)
                print("EEG recording stopped and data saved.")
            else:
                print("No active recording to stop.")
        except Exception as e:
            print(f"Error stopping recording: {e}")

    def __resolve_spectrum(self):
        # existing
        pass

    def __resolve_waves(self):
        # existing
        pass
