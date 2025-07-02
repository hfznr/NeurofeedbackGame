import os
import wfdb
import numpy as np
from datetime import datetime
from neuro_impl.utils import BB_channels

class ResistanceController:
    def __init__(self, brain_bit_controller=None, resist_received_callback=None):
        self.saved_data_dir = "./wfdb_data"
        os.makedirs(self.saved_data_dir, exist_ok=True)

        self.is_recording = False
        # store tuples: (timestamp_dt, value, quality)
        self.resistance_data = {ch: [] for ch in BB_channels}
        self.brain_bit_controller = brain_bit_controller
        self.resist_received_callback = resist_received_callback

    def start_recording(self):
        """Start recording resistance data and clear previous data."""
        try:
            self.is_recording = True
            self.resistance_data = {ch: [] for ch in BB_channels}
            print("Resistance recording started...")
        except Exception as e:
            print(f"Error starting resistance recording: {e}")

    def stop_recording(self):
        """Stop recording and save resistance data with a timestamp channel to WFDB."""
        try:
            if not self.is_recording:
                print("No active resistance recording to stop.")
                return
            self.is_recording = False
            self.save_as_wfdb(name="resistance_recording")
            print("Resistance recording stopped and data saved.")
        except Exception as e:
            print(f"Error stopping resistance recording: {e}")

    def process_resistance(self, resist):
        """Process and store resistance data with timestamp and quality."""
        print("Processing resistance data,", resist)
        if not self.is_recording:
            return
        # ts = datetime.now()
        # for ch in BB_channels:
        #     val = getattr(resist, ch, None)
        #     quality = 'Good' if val is not None and val != float('inf') and val > 2_000_000 else 'Poor'
        #     self.resistance_data[ch].append((ts, val, quality))
        #     print(f"Resistance data for {ch}: {val} ({quality})")
        if self.resist_received_callback:
            self.resist_received_callback(resist)

    def save_as_wfdb(self, name="resistance_recording"):
        """Save resistance data and time offsets as WFDB record (Time last)."""
        try:
            record_path = os.path.join(self.saved_data_dir, name)
            # prepare base time
            times = [item[0] for item in self.resistance_data[BB_channels[0]]]
            if not times:
                print("No resistance data to save.")
                return
            t0 = times[0]
            # convert to seconds offset
            time_offsets = [(t - t0).total_seconds() for t in times]

            # build binary signals for each channel
            binary_signals = []
            for ch in BB_channels:
                binary_signals.append([
                    1 if quality == 'Good' else 0
                    for (_, _, quality) in self.resistance_data[ch]
                ])

            # put the channel data first, then time last
            channels = binary_signals + [time_offsets]
            signals = np.array(channels, dtype=np.float32).T

            # units & names: one per channel in the same order
            units     = ['Binary'] * len(BB_channels) + ['s']
            sig_names = list(BB_channels)     + ['Time']
            fmts      = ['16'] * signals.shape[1]

            wfdb.wrsamp(
                record_name=name,
                fs=250,
                units=units,
                sig_name=sig_names,
                p_signal=signals,
                fmt=fmts,
                write_dir=self.saved_data_dir,
            )
            print(f"Resistance data with timestamps saved as WFDB at {record_path}")
        except Exception as e:
            print(f"Error saving resistance data: {e}")


    def start_resist(self):
        """Start resistance measurement and recording."""
        try:
            if self.brain_bit_controller:
                self.brain_bit_controller.resistReceived = self.process_resistance
                self.brain_bit_controller.start_resist()
        except Exception as e:
            print(f"Error starting resistance measurement: {e}")

    def stop_resist(self):
        """Stop resistance measurement and recording."""
        try:
            if self.brain_bit_controller:
                self.brain_bit_controller.stop_resist()
                self.brain_bit_controller.resistReceived = None
        except Exception as e:
            print(f"Error stopping resistance measurement: {e}")
