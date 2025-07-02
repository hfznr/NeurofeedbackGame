from neuro_impl.utils import BB_channels
import logging

# Configure logging
logging.basicConfig(
    filename='signal_resistance_controller.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SignalResistanceController:
    def __init__(self, brain_bit_controller=None, signal_resist_received_callback=None):
        self.brain_bit_controller = brain_bit_controller
        self.signal_resist_received_callback = signal_resist_received_callback
        self.is_recording = False
        self.signal_data = {channel: [] for channel in BB_channels}
        self.resistance_data = {channel: [] for channel in BB_channels}

    def start_recording(self):
        """Start recording signal and resistance data."""
        try:
            self.is_recording = True
            self.signal_data = {channel: [] for channel in BB_channels}
            self.resistance_data = {channel: [] for channel in BB_channels}
            logging.info("Signal and resistance recording started.")
            print("Signal and resistance recording started...")
        except Exception as e:
            logging.error(f"Error starting signal and resistance recording: {e}")
            print(f"Error starting signal and resistance recording: {e}")

    def stop_recording(self):
        """Stop recording signal and resistance data."""
        try:
            if self.is_recording:
                self.is_recording = False
                logging.info("Signal and resistance recording stopped.")
                print("Signal and resistance recording stopped.")
            else:
                logging.warning("No active signal and resistance recording to stop.")
                print("No active signal and resistance recording to stop.")
        except Exception as e:
            logging.error(f"Error stopping signal and resistance recording: {e}")
            print(f"Error stopping signal and resistance recording: {e}")

    def process_signal_resistance(self, signal, resistance):
        """Process and store signal and resistance data."""
        try:
            if self.is_recording:
                for channel in BB_channels:
                    self.signal_data[channel].append(signal[channel])
                    self.resistance_data[channel].append(resistance[channel])
                logging.debug(f"Processed signal and resistance data: {signal}, {resistance}")
                if self.signal_resist_received_callback:
                    self.signal_resist_received_callback(signal, resistance)
        except Exception as e:
            logging.error(f"Error processing signal and resistance data: {e}")
            print(f"Error processing signal and resistance data: {e}")

    def start_signal_resist(self):
        """Start signal and resistance measurement."""
        try:
            self.brain_bit_controller.signalResistReceived = self.signal_resist_received
            self.brain_bit_controller.start_signal_and_resist()
            logging.info("Signal and resistance measurement started.")
        except Exception as e:
            logging.error(f"Error starting signal and resistance measurement: {e}")
            print(f"Error starting signal and resistance measurement: {e}")

    def stop_signal_resist(self):
        """Stop signal and resistance measurement."""
        try:
            self.brain_bit_controller.stop_signal_and_resist()
            self.brain_bit_controller.signalResistReceived = None
            logging.info("Signal and resistance measurement stopped.")
        except Exception as e:
            logging.error(f"Error stopping signal and resistance measurement: {e}")
            print(f"Error stopping signal and resistance measurement: {e}")

    def signal_resist_received(self, signal, resistance):
        """Handle received signal and resistance data."""
        try:
            self.process_signal_resistance(signal, resistance)
        except Exception as e:
            logging.error(f"Error in signal_resist_received: {e}")
            print(f"Error in signal_resist_received: {e}")