
from neuro_impl.spectrum_controller import SpectrumController
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi
from ui.plots import SpectrumPlot

class SpectrumScreen(QMainWindow):
    def __init__(self, brain_bit_controller,stack_navigation, history_stack,*args, **kwargs):
        super().__init__(*args, **kwargs)
       
        self.brain_bit_controller = brain_bit_controller
        self.stack_navigation = stack_navigation
        self.history_stack = history_stack
        
        loadUi("ui/SpectrumScreenUI.ui", self)
        self.backButton.clicked.connect(self.__close_screen)
        self.signalButton.clicked.connect(self.__start_button_clicked)
        
        self.o1Graph = SpectrumPlot()
        self.o2Graph = SpectrumPlot()
        self.t3Graph = SpectrumPlot()
        self.t4Graph = SpectrumPlot()
        self.o1_graphLayout.addWidget(self.o1Graph)
        self.o2_graphLayout.addWidget(self.o2Graph)
        self.t3_graphLayout.addWidget(self.t3Graph)
        self.t4_graphLayout.addWidget(self.t4Graph)
        self.__is_started = False

        self.spectrumController = SpectrumController()
        self.spectrumController.processedWaves = self.__processed_waves
        self.spectrumController.processedSpectrum = self.__processed_spectrum

    def __start_button_clicked(self):
        if self.__is_started:
            self.__stop_recording()
            self.__stop_signal()
        else:
            self.__start_signal()
            self.__start_recording()

    def __start_signal(self):
        self.signalButton.setText('Stop')
        self.o1Graph.start_draw()
        self.o2Graph.start_draw()
        self.t3Graph.start_draw()
        self.t4Graph.start_draw()
        self.brain_bit_controller.signalReceived = self.__signal_received
        self.brain_bit_controller.start_signal()
        self.__is_started = True

    def __stop_signal(self):
        self.signalButton.setText('Start')
        self.o1Graph.stop_draw()
        self.o2Graph.stop_draw()
        self.t3Graph.stop_draw()
        self.t4Graph.stop_draw()
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None
        self.__is_started = False
        
        
    def __start_recording(self):
        """Starts recording via the SpectrumController."""
        self.spectrumController.start_recording()
        print("Recording started...")

    def __stop_recording(self):
        """Stops recording and saves the data."""
        self.spectrumController.stop_recording()
        print("Recording stopped.")
        

    def __signal_received(self, signal):
        self.spectrumController.process_data(signal)

    def __processed_waves(self, waves, channel):
        match channel:
            case 'O1':
                self.o1_alpha_raw.setText(str(round(waves.alpha_raw, 4)))
                self.o1_beta_raw.setText(str(round(waves.beta_raw, 4)))
                self.o1_theta_raw.setText(str(round(waves.theta_raw, 4)))
                self.o1_delta_raw.setText(str(round(waves.delta_raw, 4)))
                self.o1_gamma_raw.setText(str(round(waves.gamma_raw, 4)))
                self.o1_alpha_percent.setText(str(round(waves.alpha_rel * 100)) + '%')
                self.o1_beta_percent.setText(str(round(waves.beta_rel * 100)) + '%')
                self.o1_theta_percent.setText(str(round(waves.theta_rel * 100)) + '%')
                self.o1_delta_percent.setText(str(round(waves.delta_rel * 100)) + '%')
                self.o1_gamma_percent.setText(str(round(waves.gamma_rel * 100)) + '%')
            case 'O2':
                self.o2_alpha_raw.setText(str(round(waves.alpha_raw, 4)))
                self.o2_beta_raw.setText(str(round(waves.beta_raw, 4)))
                self.o2_theta_raw.setText(str(round(waves.theta_raw, 4)))
                self.o2_delta_raw.setText(str(round(waves.delta_raw, 4)))
                self.o2_gamma_raw.setText(str(round(waves.gamma_raw, 4)))
                self.o2_alpha_percent.setText(str(round(waves.alpha_rel * 100)) + '%')
                self.o2_beta_percent.setText(str(round(waves.beta_rel * 100)) + '%')
                self.o2_theta_percent.setText(str(round(waves.theta_rel * 100)) + '%')
                self.o2_delta_percent.setText(str(round(waves.delta_rel * 100)) + '%')
                self.o2_gamma_percent.setText(str(round(waves.gamma_rel * 100)) + '%')
            case 'T3':
                self.t3_alpha_raw.setText(str(round(waves.alpha_raw, 4)))
                self.t3_beta_raw.setText(str(round(waves.beta_raw, 4)))
                self.t3_theta_raw.setText(str(round(waves.theta_raw, 4)))
                self.t3_delta_raw.setText(str(round(waves.delta_raw, 4)))
                self.t3_gamma_raw.setText(str(round(waves.gamma_raw, 4)))
                self.t3_alpha_percent.setText(str(round(waves.alpha_rel * 100)) + '%')
                self.t3_beta_percent.setText(str(round(waves.beta_rel * 100)) + '%')
                self.t3_theta_percent.setText(str(round(waves.theta_rel * 100)) + '%')
                self.t3_delta_percent.setText(str(round(waves.delta_rel * 100)) + '%')
                self.t3_gamma_percent.setText(str(round(waves.gamma_rel * 100)) + '%')
            case 'T4':
                self.t4_alpha_raw.setText(str(round(waves.alpha_raw, 4)))
                self.t4_beta_raw.setText(str(round(waves.beta_raw, 4)))
                self.t4_theta_raw.setText(str(round(waves.theta_raw, 4)))
                self.t4_delta_raw.setText(str(round(waves.delta_raw, 4)))
                self.t4_gamma_raw.setText(str(round(waves.gamma_raw, 4)))
                self.t4_alpha_percent.setText(str(round(waves.alpha_rel * 100)) + '%')
                self.t4_beta_percent.setText(str(round(waves.beta_rel * 100)) + '%')
                self.t4_theta_percent.setText(str(round(waves.theta_rel * 100)) + '%')
                self.t4_delta_percent.setText(str(round(waves.delta_rel * 100)) + '%')
                self.t4_gamma_percent.setText(str(round(waves.gamma_rel * 100)) + '%')
            case _:
                print('Unknown channel')

    def __processed_spectrum(self, spectrum, channel):
        match channel:
            case 'O1':
                self.o1Graph.update_data(spectrum)
            case 'O2':
                self.o2Graph.update_data(spectrum)
            case 'T3':
                self.t3Graph.update_data(spectrum)
            case 'T4':
                self.t4Graph.update_data(spectrum)
            case _:
                print('Unknown channel')

    def __close_screen(self):
        self.__stop_signal()
        if self.history_stack:
            previous_screen = self.history_stack.pop()  # Get the last visited screen
            self.stack_navigation.setCurrentWidget(previous_screen)