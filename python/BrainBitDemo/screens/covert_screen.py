from screens.covert_widget import CovertWidget
from neuro_impl.spectrum_controller import SpectrumController
from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from PyQt6.QtCore import QTimer
from screens.gaze_thread import GazeThread


class CovertScreen(QMainWindow):
    def __init__(self, brain_bit_controller, stack_navigation, history_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.brain_bit_controller = brain_bit_controller
        self.stack_navigation = stack_navigation
        self.history_stack = history_stack
        self.setWindowTitle("Black & White Flickering Screen")
        self.setGeometry(100, 100, 600, 600)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.spectrumController = SpectrumController()
        self.__is_started = False
        self.gaze_thread = None  # Gaze tracking thread

        self.flicker_widget = CovertWidget(frequency=1.7, flicker_area_percentage=0.25, parent=self)
        layout.addWidget(self.flicker_widget)

        input_layout = QHBoxLayout()

        self.frequency_input = QLineEdit(self)
        self.frequency_input.setPlaceholderText("Enter frequency (e.g., 1.7)")
        input_layout.addWidget(self.frequency_input)

        self.flicker_area_input = QLineEdit(self)
        self.flicker_area_input.setPlaceholderText("Enter flicker area (0–1)")
        input_layout.addWidget(self.flicker_area_input)

        self.location_of_flicker = QLineEdit(self)
        self.location_of_flicker.setPlaceholderText("l = left, m = mid, r = right")
        input_layout.addWidget(self.location_of_flicker)

        layout.addLayout(input_layout)

        self.start_button = QPushButton("Start Flickering")
        self.back_button = QPushButton("Back")
        layout.addWidget(self.start_button)
        layout.addWidget(self.back_button)

        self.start_button.clicked.connect(self.__start_button_clicked)
        self.back_button.clicked.connect(self.__close_screen)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__switch_frequency)
        self.current_phase = 0

        self.phases = [
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0, "duration": 10},
        ]

    
    def __handle_gaze_direction(self, direction):
        """
        Callback to handle gaze direction updates from GazeThread.
        """
        print(f"[Gaze] Looking: {direction}")
        try:
            # Save gaze direction using SpectrumController
            self.spectrumController.update_labels(direction)
            self.spectrumController.process_data(direction)
        except Exception as e:
            print(f"Error handling gaze direction: {e}")

  
        

    def start_flickering_sequence(self):
        try:
            self.current_phase = 0
            self.__apply_phase()
            self.timer.start(1000 * self.phases[self.current_phase]["duration"])
        except Exception as e:
            print(f"Error starting flickering sequence: {e}")

    def __apply_phase(self):
        try:
            phase = self.phases[self.current_phase]
            if phase["frequency"] == 0:
                self.flicker_widget.stop_flickering()
            else:
                user_frequency = self.frequency_input.text()
                if user_frequency:
                    try:
                        phase["frequency"] = float(user_frequency)
                    except ValueError:
                        print("Invalid frequency input.")
                        return
                self.flicker_widget.set_frequency(phase["frequency"])
                self.flicker_widget.start_flickering()
        except Exception as e:
            print(f"Error applying flickering phase: {e}")

    def __switch_frequency(self):
        try:
            self.current_phase += 1
            if self.current_phase < len(self.phases):
                self.__apply_phase()
                self.timer.start(1000 * self.phases[self.current_phase]["duration"])
            else:
                self.__stop_signal()
                self.timer.stop()
                self.flicker_widget.stop_flickering()
                self.__stop_recording()
        except Exception as e:
            print(f"Error switching phase: {e}")

    def __start_button_clicked(self):
        try:
            self.start_flickering_sequence()

            flicker_area_location = self.location_of_flicker.text().strip()
            if flicker_area_location:
                self.flicker_widget.flicker_area_location = flicker_area_location
                self.flicker_widget.update_flicker_area()

            flicker_area_percentage = self.flicker_area_input.text().strip()
            if flicker_area_percentage:
                try:
                    flicker_area_percentage = float(flicker_area_percentage)
                    if 0 <= flicker_area_percentage <= 1:
                        self.flicker_widget.flicker_area_percentage = flicker_area_percentage
                        self.flicker_widget.update_flicker_area()
                    else:
                        print("Please enter a percentage between 0 and 1.")
                        return
                except ValueError:
                    print("Invalid flicker area input.")
                    return

            if self.__is_started:
                self.__stop_recording()
                self.__stop_signal()
            else:
                self.__start_signal()
                self.__start_recording()
        except Exception as e:
            print(f"Error handling start button: {e}")

    def __start_signal(self):
        try:
            # Start the gaze tracking thread before starting the signal
            if self.gaze_thread is None:
                self.gaze_thread = GazeThread(callback=self.__handle_gaze_direction)
                self.gaze_thread.start()
                print("Gaze tracking thread started.")

            # Update button text and start the signal
            self.start_button.setText('Stop')
            self.brain_bit_controller.signalReceived = self.__signal_received
            self.brain_bit_controller.start_signal()
            self.__start_recording()  # Start recording here
            self.start_flickering_sequence()
            self.__is_started = True
        except Exception as e:
            print(f"Error starting signal: {e}")

    def __stop_signal(self):
        try:
            self.start_button.setText('Start')
            self.brain_bit_controller.stop_signal()
            self.brain_bit_controller.signalReceived = None
            self.__is_started = False

            # Stop the gaze tracking thread
            if self.gaze_thread:
                self.gaze_thread.stop()
                self.gaze_thread.join()
                self.gaze_thread = None
                print("Gaze tracking thread stopped.")
        except Exception as e:
            print(f"Error stopping signal: {e}")

    def __start_recording(self):
        try:
            self.spectrumController.start_recording()
            print("Recording started...")
        except Exception as e:
            print(f"Error starting recording: {e}")

    def __stop_recording(self):
        try:
            self.spectrumController.stop_recording()
            print("Recording stopped.")
        except Exception as e:
            print(f"Error stopping recording: {e}")

    def __signal_received(self, signal):
        try:
            if self.current_phase < len(self.phases):
                phase = self.phases[self.current_phase]
                self.spectrumController.update_labels(phase["frequency"])
            self.spectrumController.process_data(signal)
        except Exception as e:
            print(f"Error processing received signal: {e}")

    def __close_screen(self):
        try:
            self.timer.stop()
            self.flicker_widget.stop_flickering()

            # Stop the gaze tracking thread
            if self.gaze_thread:
                self.gaze_thread.stop()
                self.gaze_thread.join()
                self.gaze_thread = None

            if self.history_stack:
                previous_screen = self.history_stack.pop()
                self.stack_navigation.setCurrentWidget(previous_screen)
        except Exception as e:
            print(f"Error closing screen: {e}")
