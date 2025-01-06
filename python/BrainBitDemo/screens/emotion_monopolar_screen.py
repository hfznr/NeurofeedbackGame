from neuro_impl.emotions_monopolar_controller import EmotionMonopolar



from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi


class EmotionMonopolarScreen(QMainWindow):
    def __init__(self,brain_bit_controller, stack_navigation, history_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/EmotionMonopolarScreenUI.ui", self)
        self.brain_bit_controller = brain_bit_controller
        self.stack_navigation = stack_navigation
        self.history_stack = history_stack
        self.backButton.clicked.connect(self.__close_screen)
        self.startEmotionButton.clicked.connect(self.__start_calibration)
        self.is_started = False

        self.emotionController = EmotionMonopolar()
        self.emotionController.progressCalibrationCallback = self.calibration_callback
        self.emotionController.isArtifactedSequenceCallback = self.is_artifacted_sequence_callback
        self.emotionController.isBothSidesArtifactedCallback = self.is_both_sides_artifacted_callback
        self.emotionController.lastMindDataCallback = self.mind_data_callback
        self.emotionController.lastSpectralDataCallback = self.last_spectral_data_callback
        self.emotionController.rawSpectralDataCallback = self.raw_spectral_data_callback

    def __start_calibration(self):
        if self.is_started:
            self.__stop_signal()
        else:
            self.__start_signal()

    def __start_signal(self):
        self.startEmotionButton.setText('Stop')
        self.emotionController.start_calibration()
        self.brain_bit_controller.signalReceived = self.emotionController.process_data
        self.brain_bit_controller.start_signal()
        self.is_started = True

    def __stop_signal(self):
        self.startEmotionButton.setText('Start')
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None
        self.is_started = False

    def calibration_callback(self, progress, channel):
        match channel:
            case 'O1':
                self.o1calibrationProgress.setValue(progress)
            case 'O2':
                self.o2calibrationProgress.setValue(progress)
            case 'T3':
                self.t3calibrationProgress.setValue(progress)
            case 'T4':
                self.t4calibrationProgress.setValue(progress)
            case _:
                print('Unknown channel')

    def is_artifacted_sequence_callback(self, artifacted, channel):
        match channel:
            case 'O1':
                self.o1artSequenceLabel.setText('Artefacted sequence: ' + str(artifacted))
            case 'O2':
                self.o2artSequenceLabel.setText('Artefacted sequence: ' + str(artifacted))
            case 'T3':
                self.t3artSequenceLabel.setText('Artefacted sequence: ' + str(artifacted))
            case 'T4':
                self.t4artSequenceLabel.setText('Artefacted sequence: ' + str(artifacted))
            case _:
                print('Unknown channel')

    def is_both_sides_artifacted_callback(self, artifacted, channel):
        match channel:
            case 'O1':
                self.o1artBothSidesLabel.setText('Artefacted both side: ' + str(artifacted))
            case 'O2':
                self.o2artBothSidesLabel.setText('Artefacted both side: ' + str(artifacted))
            case 'T3':
                self.t3artBothSidesLabel.setText('Artefacted both side: ' + str(artifacted))
            case 'T4':
                self.t4artBothSidesLabel.setText('Artefacted both side: ' + str(artifacted))
            case _:
                print('Unknown channel')

    def mind_data_callback(self, data, channel):
        match channel:
            case 'O1':
                self.o1attentionPercentLabel.setText(str(round(data.rel_attention, 2)))
                self.o1relaxPercentLabel.setText(str(round(data.rel_relaxation, 2)))
                self.o1attentionRawLabel.setText(str(round(data.inst_attention, 2)))
                self.o1relaxRawLabel.setText(str(round(data.inst_relaxation, 2)))
            case 'O2':
                self.o2attentionPercentLabel.setText(str(round(data.rel_attention, 2)))
                self.o2relaxPercentLabel.setText(str(round(data.rel_relaxation, 2)))
                self.o2attentionRawLabel.setText(str(round(data.inst_attention, 2)))
                self.o2relaxRawLabel.setText(str(round(data.inst_relaxation, 2)))
            case 'T3':
                self.t3attentionPercentLabel.setText(str(round(data.rel_attention, 2)))
                self.t3relaxPercentLabel.setText(str(round(data.rel_relaxation, 2)))
                self.t3attentionRawLabel.setText(str(round(data.inst_attention, 2)))
                self.t3relaxRawLabel.setText(str(round(data.inst_relaxation, 2)))
            case 'T4':
                self.t4attentionPercentLabel.setText(str(round(data.rel_attention, 2)))
                self.t4relaxPercentLabel.setText(str(round(data.rel_relaxation, 2)))
                self.t4attentionRawLabel.setText(str(round(data.inst_attention, 2)))
                self.t4relaxRawLabel.setText(str(round(data.inst_relaxation, 2)))
            case _:
                print('Unknown channel')

    def last_spectral_data_callback(self, spectral_data, channel):
        match channel:
            case 'O1':
                self.o1deltaPercentLabel.setText(str(round(spectral_data.delta * 100, 2)) + '%')
                self.o1thetaPercentLabel.setText(str(round(spectral_data.theta * 100, 2)) + '%')
                self.o1alphaPercentLabel.setText(str(round(spectral_data.alpha * 100, 2)) + '%')
                self.o1betaPercentLabel.setText(str(round(spectral_data.beta * 100, 2)) + '%')
                self.o1gammaPercentLabel.setText(str(round(spectral_data.gamma * 100, 2)) + '%')
            case 'O2':
                self.o2deltaPercentLabel.setText(str(round(spectral_data.delta * 100, 2)) + '%')
                self.o2thetaPercentLabel.setText(str(round(spectral_data.theta * 100, 2)) + '%')
                self.o2alphaPercentLabel.setText(str(round(spectral_data.alpha * 100, 2)) + '%')
                self.o2betaPercentLabel.setText(str(round(spectral_data.beta * 100, 2)) + '%')
                self.o2gammaPercentLabel.setText(str(round(spectral_data.gamma * 100, 2)) + '%')
            case 'T3':
                self.t3deltaPercentLabel.setText(str(round(spectral_data.delta * 100, 2)) + '%')
                self.t3thetaPercentLabel.setText(str(round(spectral_data.theta * 100, 2)) + '%')
                self.t3alphaPercentLabel.setText(str(round(spectral_data.alpha * 100, 2)) + '%')
                self.t3betaPercentLabel.setText(str(round(spectral_data.beta * 100, 2)) + '%')
                self.t3gammaPercentLabel.setText(str(round(spectral_data.gamma * 100, 2)) + '%')
            case 'T4':
                self.t4deltaPercentLabel.setText(str(round(spectral_data.delta * 100, 2)) + '%')
                self.t4thetaPercentLabel.setText(str(round(spectral_data.theta * 100, 2)) + '%')
                self.t4alphaPercentLabel.setText(str(round(spectral_data.alpha * 100, 2)) + '%')
                self.t4betaPercentLabel.setText(str(round(spectral_data.beta * 100, 2)) + '%')
                self.t4gammaPercentLabel.setText(str(round(spectral_data.gamma * 100, 2)) + '%')
            case _:
                print('Unknown channel')

    def raw_spectral_data_callback(self, spect_vals, channel):
        match channel:
            case 'O1':
                self.o1alphaRawLabel.setText(str(round(spect_vals.alpha, 2)))
                self.o1betaRawLabel.setText(str(round(spect_vals.beta, 2)))
            case 'O2':
                self.o2alphaRawLabel.setText(str(round(spect_vals.alpha, 2)))
                self.o2betaRawLabel.setText(str(round(spect_vals.beta, 2)))
            case 'T3':
                self.t3alphaRawLabel.setText(str(round(spect_vals.alpha, 2)))
                self.t3betaRawLabel.setText(str(round(spect_vals.beta, 2)))
            case 'T4':
                self.t4alphaRawLabel.setText(str(round(spect_vals.alpha, 2)))
                self.t4betaRawLabel.setText(str(round(spect_vals.beta, 2)))
            case _:
                print('Unknown channel')

    def __close_screen(self):
        self.__stop_signal()
        if self.history_stack:
            previous_screen = self.history_stack.pop()  # Get the last visited screen
            self.stack_navigation.setCurrentWidget(previous_screen)

