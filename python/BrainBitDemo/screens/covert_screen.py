import logging
import time
from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from PyQt6.QtCore import QTimer

from screens.covert_widget import CovertWidget
from neuro_impl.spectrum_controller import SpectrumController
from neuro_impl.resistance_controller import ResistanceController

# Configure logging
logging.basicConfig(
    filename='covert_screen.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CovertScreen(QMainWindow):
    def __init__(self, brain_bit_controller, stack_navigation, history_stack, send_gaze_command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brain_bit_controller = brain_bit_controller
        self.stack_navigation     = stack_navigation
        self.history_stack        = history_stack
        self.send_gaze_command    = send_gaze_command

        self.setWindowTitle("Black & White Flickering Screen")
        self.setGeometry(100, 100, 600, 600)

        # Controllers
        self.spectrumController   = SpectrumController()
        self.resistanceController = ResistanceController(
            brain_bit_controller=brain_bit_controller,
            resist_received_callback=self.resist_received
        )

        # State flags
        self.__is_started     = False  # for Start Flickering
        self.__is_interleaved = False  # for interleaved mode

        # Interleaved parameters
        self.burst_secs    = 0.2
        self.interval_secs = 1.0

        # Build UI
        central = QWidget()
        layout  = QVBoxLayout(central)
        self.setCentralWidget(central)

        # Flicker widget
        self.flicker_widget = CovertWidget(frequency=1.7, flicker_area_percentage=0.25, parent=self)
        layout.addWidget(self.flicker_widget)

        # Inputs: frequency, area, location
        input_layout = QHBoxLayout()
        self.frequency_input     = QLineEdit(self); self.frequency_input.setPlaceholderText("1.7 Hz")
        self.flicker_area_input  = QLineEdit(self); self.flicker_area_input.setPlaceholderText("0–1 area")
        self.location_of_flicker = QLineEdit(self); self.location_of_flicker.setPlaceholderText("l/m/r")
        self.name_input          = QLineEdit(self); self.name_input.setPlaceholderText("name")
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.frequency_input)
        input_layout.addWidget(self.flicker_area_input)
        input_layout.addWidget(self.location_of_flicker)
        layout.addLayout(input_layout)

        # Buttons
        self.start_button       = QPushButton("Start Flickering")
        self.interleaved_button = QPushButton("Start Interleaved")
        self.back_button        = QPushButton("Back")
        layout.addWidget(self.start_button)
        layout.addWidget(self.interleaved_button)
        layout.addWidget(self.back_button)

        # Hook buttons
        self.start_button.clicked.connect(self.__start_button_clicked)
        self.interleaved_button.clicked.connect(self.__toggle_interleaved)
        self.back_button.clicked.connect(self.__close_screen)

        # Flicker-phase timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.__switch_frequency)
        self.current_phase = 0
        self.phases = [
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0.0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0.0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0.0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0.0, "duration": 10},
            {"frequency": 1.7, "duration": 30},
            {"frequency": 0.0, "duration": 10},
        ]

    # — Flicker sequence — #
    def start_flickering_sequence(self):
        self.current_phase = 0
        self.__apply_phase()
        dur = self.phases[0]["duration"]
        self.timer.start(int(1000 * dur))

    def __apply_phase(self):
        ph = self.phases[self.current_phase]
        if ph["frequency"] == 0:
            self.flicker_widget.stop_flickering()
        else:
            txt = self.frequency_input.text().strip()
            if txt:
                try: ph["frequency"] = float(txt)
                except: pass
            self.flicker_widget.set_frequency(ph["frequency"])
            self.flicker_widget.start_flickering()

    def __switch_frequency(self):
        self.current_phase += 1
        if self.current_phase < len(self.phases):
            self.__apply_phase()
            dur = self.phases[self.current_phase]["duration"]
            self.timer.start(int(1000 * dur))
        else:
            self.timer.stop()
            self.flicker_widget.stop_flickering()
            if self.__is_started:
                self.__stop_signal()
                self.__stop_recording()

    # — Start/stop flicker + EEG — #
    def __start_button_clicked(self):
        # apply flicker inputs
        loc  = self.location_of_flicker.text().strip()
        area = self.flicker_area_input.text().strip()
        if loc:
            self.flicker_widget.flicker_area_location = loc
            self.flicker_widget.update_flicker_area()
        if area:
            try:
                a = float(area)
                if 0<=a<=1:
                    self.flicker_widget.flicker_area_percentage = a
                    self.flicker_widget.update_flicker_area()
            except: pass

        if self.__is_started:
            self.timer.stop()
            self.flicker_widget.stop_flickering()
            self.__stop_signal()
            self.__stop_recording()
            self.start_button.setText("Start Flickering")
            self.__is_started = False
        else:
            self.start_flickering_sequence()
            self.__start_signal()
            self.__start_recording()
            self.start_button.setText("Stop Flickering")
            self.__is_started = True

    def __start_signal(self):
        self.brain_bit_controller.signalReceived = self.__signal_received
        self.brain_bit_controller.start_signal()
        self.__is_started = True
        self.start_button.setText("Stop Flickering")

    def __stop_signal(self):
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None
        # Also ensure interleaved stopped
        self.brain_bit_controller.stop_interleaved()
        self.brain_bit_controller.resistReceived = None
        self.__is_started = False
        self.start_button.setText("Start Flickering")

    # — Recording — #
    def __start_recording(self):
        self.send_gaze_command("start recording")
        self.spectrumController.start_recording()
        #self.resistanceController.start_recording()
        
    def get_path(self):
        name = self.name_input.text().strip() or "experiment"
        frequency = self.frequency_input.text().strip() or "1_7"
        loc  = self.location_of_flicker.text().strip() or "m"
        area = self.flicker_area_input.text().strip() or "0.25"
        # Replace '.' with '_' in all components
        name = name.replace('.', '_')
        frequency = frequency.replace('.', '_')
        loc = loc.replace('.', '_')
        area = area.replace('.', '_')
        path = f"data/{name}/{frequency}/{frequency}_{loc}_{area}"
        return path

    def __stop_recording(self):
        path = self.get_path()
        self.spectrumController.stop_recording(path = path)
        #self.resistanceController.stop_recording()
        self.send_gaze_command("stop recording")

    # — EEG callback — #
    def __signal_received(self, signal):
        if self.current_phase < len(self.phases):
            freq = self.phases[self.current_phase]["frequency"]
            self.spectrumController.update_labels(freq)
        self.spectrumController.process_data(signal)

    # — Interleaved EEG + impedance — #
    def __toggle_interleaved(self):
        if not self.__is_interleaved:
            # apply flicker inputs
            loc  = self.location_of_flicker.text().strip()
            area = self.flicker_area_input.text().strip()
            freq = self.frequency_input.text().strip()
            if loc:
                self.flicker_widget.flicker_area_location = loc
                self.flicker_widget.update_flicker_area()
            if area:
                try:
                    a = float(area)
                    if 0<=a<=1:
                        self.flicker_widget.flicker_area_percentage = a
                        self.flicker_widget.update_flicker_area()
                except: pass
            if freq:
                try: self.flicker_widget.set_frequency(float(freq))
                except: pass

            # start flicker phases
            self.start_flickering_sequence()

            # hook callbacks
            self.brain_bit_controller.signalReceived = self.__signal_received
            self.brain_bit_controller.resistReceived = self.resist_received

            # start interleaved loop
            self.brain_bit_controller.start_interleaved(
                burst_secs    = self.burst_secs,
                interval_secs = self.interval_secs
            )
            self.__start_recording()

            self.interleaved_button.setText("Stop Interleaved")
            self.__is_interleaved = True
        else:
            self.brain_bit_controller.stop_interleaved()
            self.brain_bit_controller.signalReceived = None
            self.brain_bit_controller.resistReceived = None

            self.timer.stop()
            self.flicker_widget.stop_flickering()
            self.__stop_recording()

            self.interleaved_button.setText("Start Interleaved")
            self.__is_interleaved = False

    def resist_received(self, resist):
        self.resistanceController.process_resistance(resist)

    # — Navigation & cleanup — #
    def __close_screen(self):
        self.timer.stop()
        self.flicker_widget.stop_flickering()
        if self.__is_started:
            self.__stop_signal()
            self.__stop_recording()
        if self.__is_interleaved:
            self.brain_bit_controller.stop_interleaved()
        if self.history_stack:
            prev = self.history_stack.pop()
            self.stack_navigation.setCurrentWidget(prev)

    def closeEvent(self, event):
        if self.__is_started:
            self.__stop_signal()
            self.__stop_recording()
        if self.__is_interleaved:
            self.brain_bit_controller.stop_interleaved()
        super().closeEvent(event)
