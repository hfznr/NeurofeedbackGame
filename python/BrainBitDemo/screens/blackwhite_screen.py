from screens.blackwhite_widget import BlackWhiteWidget
from neuro_impl.spectrum_controller import SpectrumController
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLineEdit
from PyQt6.QtCore import QTimer

class BlackWhiteScreen(QMainWindow):
    def __init__(self, brain_bit_controller, stack_navigation, history_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.brain_bit_controller = brain_bit_controller
        self.stack_navigation = stack_navigation
        self.history_stack = history_stack
        self.setWindowTitle("Black & White Flickering Screen")
        self.setGeometry(100, 100, 600, 600)

        # Main layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Spectrum controller
        self.spectrumController = SpectrumController()
        self.__is_started = False

        # Black & White flickering widget
        self.flicker_widget = BlackWhiteWidget(frequency=1.7, flicker_area_percentage=0.25, parent=self)
        layout.addWidget(self.flicker_widget)

        # Input space above the start button for flicker area percentage
        self.flicker_area_input = QLineEdit(self)
        self.flicker_area_input.setPlaceholderText("Enter flicker area percentage (e.g., 0.25 for 25%)")  # Set a placeholder
        layout.addWidget(self.flicker_area_input)

        # Buttons
        self.start_button = QPushButton("Start Flickering")
        self.back_button = QPushButton("Back")
        layout.addWidget(self.start_button)
        layout.addWidget(self.back_button)

        # Button connections
        self.start_button.clicked.connect(self.__start_button_clicked)
        self.back_button.clicked.connect(self.__close_screen)

        # Timer to manage flickering phases
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__switch_frequency)
        self.current_phase = 0  # Tracks the current phase of the flickering sequence

        # Initial frequencies and durations for each phase
        self.phases = [ 
            {"frequency": 1.7, "duration": 30},  # Flicker #1
            {"frequency": 0, "duration": 10},  # Rest
            {"frequency": 1.7, "duration": 30},  # Flicker #2
            {"frequency": 0, "duration": 10},  
            {"frequency": 1.7, "duration": 30},  # Flicker #3
            {"frequency": 0, "duration": 10},  
            {"frequency": 1.7, "duration": 30},  # Flicker #4
            {"frequency": 0, "duration": 10},  
            {"frequency": 1.7, "duration": 30},  # Flicker #5
            {"frequency": 0, "duration": 10},  
        ]

    def start_flickering_sequence(self):
        """Start the flickering sequence."""
        try:
            self.current_phase = 0  # Reset to the first phase
            self.__apply_phase()
            self.timer.start(1000 * self.phases[self.current_phase]["duration"])  # Start the timer for the first phase
        except Exception as e:
            print(f"Error starting flickering sequence: {e}")

    def __apply_phase(self):
        """Apply the current phase settings."""
        try:
            phase = self.phases[self.current_phase]
            if phase["frequency"] == 0:
                self.flicker_widget.stop_flickering()  # No flicker
            else:
                self.flicker_widget.set_frequency(phase["frequency"])
                self.flicker_widget.start_flickering()
        except Exception as e:
            print(f"Error applying flickering phase: {e}")

    def __switch_frequency(self):
        """Switch to the next frequency phase."""
        try:
            self.current_phase += 1
            if self.current_phase < len(self.phases):
                self.__apply_phase()
                self.timer.start(1000 * self.phases[self.current_phase]["duration"])  # Start timer for the next phase
            else:
                self.__stop_signal()
                self.timer.stop()  # Stop the timer after all phases are done
                self.flicker_widget.stop_flickering()  # Stop flickering after the sequence
                self.__stop_recording()  # Stop recording after the sequence
        except Exception as e:
            print(f"Error switching frequency phase: {e}")

    def __start_button_clicked(self):
        """Handle start/stop button clicks."""
        try:
            # Get the flicker area percentage from the input field
            flicker_area_percentage = self.flicker_area_input.text()
            if flicker_area_percentage:
                try:
                    # Convert the input to a float
                    flicker_area_percentage = float(flicker_area_percentage)
                    if 0 <= flicker_area_percentage <= 1:
                        # Update the flicker widget's flicker area percentage
                        self.flicker_widget.flicker_area_percentage = flicker_area_percentage
                        self.flicker_widget.update_flicker_area()
                    else:
                        print("Please enter a percentage between 0 and 1.")
                        return
                except ValueError:
                    print("Invalid flicker area input. Please enter a valid percentage.")
                    return

            if self.__is_started:
                self.__stop_recording()
                self.__stop_signal()
            else:
                self.__start_signal()
                self.__start_recording()
        except Exception as e:
            print(f"Error handling start button: {e}")

    # Signal handling
    def __start_signal(self):
        """Start capturing signals."""
        try:
            self.start_button.setText('Stop')
            self.brain_bit_controller.signalReceived = self.__signal_received
            self.brain_bit_controller.start_signal()
            # Start the flickering sequence automatically
            self.start_flickering_sequence()
            self.__is_started = True
        except Exception as e:
            print(f"Error starting signal: {e}")

    def __stop_signal(self):
        """Stop capturing signals."""
        try:
            self.start_button.setText('Start')
            self.brain_bit_controller.stop_signal()
            self.brain_bit_controller.signalReceived = None
            self.__is_started = False
        except Exception as e:
            print(f"Error stopping signal: {e}")

    def __start_recording(self):
        """Start recording signals."""
        try:
            self.spectrumController.start_recording()
            print("Recording started...")
        except Exception as e:
            print(f"Error starting recording: {e}")

    def __stop_recording(self,path = ""):
        """Stop recording signals."""
        try:
            self.spectrumController.stop_recording(path = path)
            print("Recording stopped.")
        except Exception as e:
            print(f"Error stopping recording: {e}")

    def __signal_received(self, signal):
        """Handle received signals."""
        try:
            print(signal)
            if self.current_phase < len(self.phases):
                phase = self.phases[self.current_phase]
                self.spectrumController.update_labels(phase["frequency"])
            self.spectrumController.process_data(signal)
        except Exception as e:
            print(f"Error processing received signal: {e}")

    def __close_screen(self):
        """Handle the back button and stop any ongoing flickering."""
        try:
            self.timer.stop()  # Stop the timer if running
            self.flicker_widget.stop_flickering()
            if self.history_stack:
                previous_screen = self.history_stack.pop()  # Get the last visited screen
                self.stack_navigation.setCurrentWidget(previous_screen)
        except Exception as e:
            print(f"Error closing screen: {e}")
