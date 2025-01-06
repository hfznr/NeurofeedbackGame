from spectrum_lib.spectrum_lib import SpectrumMath
from neuro_impl.utils import BB_channels
import os
import wfdb
import numpy as np


class SpectrumController:
    def __init__(self):
        sampling_rate = 250  # raw signal sampling frequency
        fft_window = sampling_rate * 4  # spectrum calculation window length
        process_win_rate = 5  # spectrum calculation frequency
        bord_frequency = 50  # upper bound of frequencies for spectrum calculation
        normalize_spect_by_bandwidth = True  # normalization of the EEG spectrum by the width of the wavebands
        delta_coef = 0.0
        theta_coef = 1.0
        alpha_coef = 1.0
        beta_coef = 1.0
        gamma_coef = 0.0

        self.maths = {BB_channels[i]: SpectrumMath(sampling_rate, fft_window, process_win_rate) for i in range(4)}
        for i in range(4):
            self.maths[BB_channels[i]].init_params(bord_frequency, normalize_spect_by_bandwidth)
            self.maths[BB_channels[i]].set_waves_coeffs(delta_coef, theta_coef, alpha_coef, beta_coef, gamma_coef)

        self.processedSpectrum = None
        self.processedWaves = None
        
        self.saved_data_dir = "./wfdb_data"  # Directory to save WFDB files
        os.makedirs(self.saved_data_dir, exist_ok=True)  # Ensure the directory exists
        
        # Initialize raw signal storage
        self.raw_signals = {channel: [] for channel in BB_channels}  
        self.is_recording = False  # Flag to track recording status
        self.labels = []  # List to store frequency labels
        self.current_label = 0

    def process_data(self, brain_bit_data):
        try:
            o1Values, o2Values, t3Values, t4Values = [], [], [], []
            for i in range(len(brain_bit_data)):
                o1Values.append(brain_bit_data[i].O1 * 1e3)
                o2Values.append(brain_bit_data[i].O2 * 1e3)
                t3Values.append(brain_bit_data[i].T3 * 1e3)
                t4Values.append(brain_bit_data[i].T4 * 1e3)
            
            # Save raw signal data if recording
            if self.is_recording:
                self.raw_signals["O1"].extend(o1Values)
                self.raw_signals["O2"].extend(o2Values)
                self.raw_signals["T3"].extend(t3Values)
                self.raw_signals["T4"].extend(t4Values)
                # Extend labels to match the length of signals
                self.labels.extend([self.current_label] * len(o1Values))
            
            # Process data
            self.maths['O1'].push_and_process_data(o1Values)
            self.maths['O2'].push_and_process_data(o2Values)
            self.maths['T3'].push_and_process_data(t3Values)
            self.maths['T4'].push_and_process_data(t4Values)
            self.__resolve_spectrum()
            self.__resolve_waves()

            # Reset sample size after processing
            for i in range(4):
                self.maths[BB_channels[i]].set_new_sample_size()

        except Exception as e:
            print(f"Error processing data: {e}")
            
    def save_as_wfdb(self, name="eeg_recording"):
        """Saves raw signals to WFDB format."""
        file_path = os.path.join(self.saved_data_dir, name)
        
        # Combine raw signals into a multi-channel array
        signals = [
            self.raw_signals["O1"],
            self.raw_signals["O2"],
            self.raw_signals["T3"],
            self.raw_signals["T4"]
        ]
        
        # Convert to numpy array and transpose to match WFDB format
        signals = np.array(signals).T

        # Ensure there is valid data to save
        if signals.size == 0:
            print("No data to save. Recording might not have started.")
            return

        # Save the signals using wfdb
        wfdb.wrsamp(
            record_name=name,
            fs=250,  # Sampling frequency
            units=['mV', 'mV', 'mV', 'mV'],  # Units for each channel
            sig_name=['O1', 'O2', 'T3', 'T4'],  # Channel names
            p_signal=signals,  # Signal data as numpy array
            fmt=['16', '16', '16', '16'],  # Data format
            write_dir=self.saved_data_dir,  # Directory to save
        )
        print(f"Signals saved as WFDB record at {file_path}")

    def save_as_wfdb_label(self, name="eeg_recording_label"):
        """Saves frequency labels to WFDB format."""
        try:
            file_path = os.path.join(self.saved_data_dir, name)
            
            # Convert labels to a numpy array
            labels_array = np.array(self.labels, dtype=np.float32)

            # Ensure there is valid data to save
            if labels_array.size == 0:
                print("No labels to save.")
                return

            # Save the labels using wfdb
            wfdb.wrsamp(
                record_name=name,
                fs=250,  # Sampling frequency
                units=['Hz'],  # Units for each channel
                sig_name=['Frequency'],  # Channel name
                p_signal=labels_array.reshape(-1, 1),  # Signal data as numpy array
                fmt=['16'],  # Data format
                write_dir=self.saved_data_dir,  # Directory to save
            )
            print(f"Labels saved as WFDB record at {file_path}")
        except Exception as e:
            print(f"Error saving labels: {e}")

    def update_labels(self, label):
        """Update the current label."""
        try:
            self.current_label = label
        except Exception as e:
            print(f"Error updating labels: {e}")

    def start_recording(self):
        """Start recording signals and clear previous data."""
        try:
            self.is_recording = True
            self.raw_signals = {channel: [] for channel in BB_channels}  # Clear previous signal data
            self.labels = []  # Clear previous labels
            print("Recording started...")
        except Exception as e:
            print(f"Error starting recording: {e}")

    def stop_recording(self):
        """Stop recording and save the data."""
        try:
            if self.is_recording:
                self.is_recording = False
                self.save_as_wfdb(name="eeg_recording")
                self.save_as_wfdb_label(name="eeg_recording_label")
                print("Recording stopped and data saved.")
            else:
                print("No active recording to stop.")
        except Exception as e:
            print(f"Error stopping recording: {e}")

    def __resolve_spectrum(self):
        try:
            for i in range(4):
                raw_spectrum = self.maths[BB_channels[i]].read_raw_spectrum_info_arr()
                if raw_spectrum:
                    raw_data = raw_spectrum[-1].all_bins_values
                    if raw_data and self.processedSpectrum:
                        self.processedSpectrum(raw_data, BB_channels[i])
        except Exception as e:
            print(f"Error resolving spectrum: {e}")

    def __resolve_waves(self):
        try:
            for i in range(4):
                waves_spectrum = self.maths[BB_channels[i]].read_waves_spectrum_info_arr()
                if waves_spectrum and self.processedWaves:
                    self.processedWaves(waves_spectrum[-1], BB_channels[i])
        except Exception as e:
            print(f"Error resolving waves: {e}")
