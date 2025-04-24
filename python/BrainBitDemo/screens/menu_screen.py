
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi
from neurosdk.cmn_types import SensorState


class MenuScreen(QMainWindow):
    def __init__(self, brain_bit_controller,stackNavigation, history_stack,
                searchScreen, 
                resistScreen, 
                signalScreen,
                emotionBipolarScreen, 
                emotionMonopolarScreen, 
                spectrumScreen,
                chessboardScreen,
                blackWhiteScreen,
                covertScreen,
                *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        loadUi("ui/MenuScreenUI.ui", self)
        
        self.brain_bit_controller = brain_bit_controller
        self.stackNavigation = stackNavigation
        self.history_stack = history_stack
        
        self.searchScreen = searchScreen
        self.resistScreen = resistScreen
        self.signalScreen = signalScreen
        self.emotionBipolarScreen = emotionBipolarScreen
        self.emotionMonopolarScreen = emotionMonopolarScreen
        self.spectrumScreen = spectrumScreen
        self.chessboardScreen = chessboardScreen
        self.blackWhiteScreen = blackWhiteScreen
        self.covertScreen = covertScreen
        
        self.brain_bit_controller.sensorConnectionState.connect(self.is_sensor_connected)
        self.toResistButton.setEnabled(False)
        self.toSignalButton.setEnabled(False)
        self.toEmBipolarButton.setEnabled(False)
        self.toEmMonopolarButton.setEnabled(False)
        self.toSpectrumButton.setEnabled(False)
        self.toSpectrumButton.setEnabled(False)
        #self.toChessboardButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)
        self.toSearchButton.clicked.connect(self.go_to_search)
        self.toResistButton.clicked.connect(self.go_to_resist)
        self.toSignalButton.clicked.connect(self.go_to_signal)
        self.toEmBipolarButton.clicked.connect(self.go_to_emotions)
        self.toEmMonopolarButton.clicked.connect(self.go_to_monopolar_emotions)
        self.toSpectrumButton.clicked.connect(self.go_to_spectrum)
        self.toChessboardButton.clicked.connect(self.go_to_chessboard)
        self.toBlackWhiteButton.clicked.connect(self.go_to_blackwhite)
        self.toCovertButton.clicked.connect(self.go_to_covert)
        self.disconnectButton.clicked.connect(self.disconnect_sensor)

    def is_sensor_connected(self, state):
        buttons_enabled = state == SensorState.StateInRange
        self.toResistButton.setEnabled(buttons_enabled)
        self.toSignalButton.setEnabled(buttons_enabled)
        self.toEmBipolarButton.setEnabled(buttons_enabled)
        self.toEmMonopolarButton.setEnabled(buttons_enabled)
        self.toSpectrumButton.setEnabled(buttons_enabled)
        self.toChessboardButton.setEnabled(buttons_enabled)
        self.toBlackWhiteButton.setEnabled(buttons_enabled)
        self.toCovertButton.setEnabled(buttons_enabled)
        self.disconnectButton.setEnabled(buttons_enabled)

    def go_to_search(self):
        self.history_stack.append(self)
        self.stackNavigation.setCurrentWidget(self.searchScreen)

    def go_to_resist(self):
        self.history_stack.append(self)
        self.stackNavigation.setCurrentWidget(self.resistScreen)

    def go_to_signal(self):
        self.history_stack.append(self)
        self.stackNavigation.setCurrentWidget(self.signalScreen)

    def go_to_emotions(self):
        self.history_stack.append(self)
        self.stackNavigation.setCurrentWidget(self.emotionBipolarScreen)

    def go_to_monopolar_emotions(self):
        self.history_stack.append(self)
        self.stackNavigation.setCurrentWidget(self.emotionMonopolarScreen)

    def go_to_spectrum(self):
        self.history_stack.append(self)
        self.stackNavigation.setCurrentWidget(self.spectrumScreen)
        
    def go_to_chessboard(self):
        self.history_stack.append(self)  # Add current screen to history
        self.stackNavigation.setCurrentWidget(self.chessboardScreen)
        
    def go_to_blackwhite(self):
        self.history_stack.append(self)  # Add current screen to history
        self.stackNavigation.setCurrentWidget(self.blackWhiteScreen)
        
    def go_to_covert(self):
        self.history_stack.append(self)  # Add current screen to history
        self.stackNavigation.setCurrentWidget(self.covertScreen)
        
    def disconnect_sensor(self):
        """Disconnect the sensor when the button is clicked."""
        try:
            self.brain_bit_controller.stop_signal()
            self.brain_bit_controller.disconnect_sensor()
            print("Sensor disconnected successfully.")
        except Exception as e:
            print(f"Error disconnecting sensor: {e}")

    def closeEvent(self, event):
        """Handle the window close event."""
        try:
            self.brain_bit_controller.stop_signal()
            self.brain_bit_controller.disconnect_sensor()
            print("Sensor disconnected during close event.")
        except Exception as e:
            print(f"Error during disconnection: {e}")
        finally:
            del self.brain_bit_controller
            print("Brain bit controller deleted successfully.")
        event.accept()
