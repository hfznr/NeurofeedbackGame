import sys
import subprocess
import atexit
import os

from PyQt6.QtWidgets import QApplication, QStackedWidget

from neuro_impl.brain_bit_controller import brain_bit_controller

from screens.search_screen import SearchScreen
from screens.resistance_screen import ResistanceScreen
from screens.chessboard_screen import ChessboardScreen
from screens.spectrum_screen import SpectrumScreen
from screens.emotion_monopolar_screen import EmotionMonopolarScreen
from screens.emotion_bipolar_screen import EmotionBipolarScreen
from screens.signal_screen import SignalScreen
from screens.menu_screen import MenuScreen
from screens.blackwhite_screen import BlackWhiteScreen
from screens.covert_screen import CovertScreen

from gaze_command import start_gaze_process, send_gaze_command

# Start the GazeTracking subprocess
gaze_script_path = os.path.join(os.path.dirname(__file__), 'GazeTracking', 'example.py')
start_gaze_process(gaze_script_path)

# 🧠 App Setup
app = QApplication(sys.argv)
stackNavigation = QStackedWidget()
history_stack = []  # Stack to maintain the navigation history

searchScreen = SearchScreen(brain_bit_controller, stackNavigation, history_stack)
resistScreen = ResistanceScreen(brain_bit_controller, stackNavigation, history_stack)
signalScreen = SignalScreen(brain_bit_controller, stackNavigation, history_stack)
emotionBipolarScreen = EmotionBipolarScreen(brain_bit_controller, stackNavigation, history_stack)
emotionMonopolarScreen = EmotionMonopolarScreen(brain_bit_controller, stackNavigation, history_stack)
spectrumScreen = SpectrumScreen(brain_bit_controller, stackNavigation, history_stack)
chessboardScreen = ChessboardScreen(brain_bit_controller, stackNavigation, history_stack)
blackWhiteScreen = BlackWhiteScreen(brain_bit_controller, stackNavigation, history_stack)
covertScreen = CovertScreen(brain_bit_controller, stackNavigation, history_stack, send_gaze_command)

menuScreen = MenuScreen(brain_bit_controller, stackNavigation, history_stack,
                        searchScreen,
                        resistScreen,
                        signalScreen,
                        emotionBipolarScreen,
                        emotionMonopolarScreen,
                        spectrumScreen,
                        chessboardScreen,
                        blackWhiteScreen,
                        covertScreen)

stackNavigation.addWidget(menuScreen)
stackNavigation.addWidget(searchScreen)
stackNavigation.addWidget(resistScreen)
stackNavigation.addWidget(signalScreen)
stackNavigation.addWidget(emotionBipolarScreen)
stackNavigation.addWidget(emotionMonopolarScreen)
stackNavigation.addWidget(spectrumScreen)
stackNavigation.addWidget(chessboardScreen)
stackNavigation.addWidget(blackWhiteScreen)
stackNavigation.addWidget(covertScreen)

stackNavigation.setCurrentWidget(menuScreen)
stackNavigation.show()

# 🧠 Start App Loop
try:
    #send_gaze_command("start recording")  # Start recording when the app starts
    app.exec()
except Exception as e:
    print(f"Error during application execution: {e}")
finally:
    try:
        print("Stopping signals...")
        #send_gaze_command("stop recording")  # Stop recording when the app exits
        brain_bit_controller.stop_signal()
        print("Disconnecting the sensor...")
        brain_bit_controller.disconnect_sensor()
    except Exception as disconnect_error:
        print(f"Error during brain_bit_controller cleanup: {disconnect_error}")
    finally:
        del brain_bit_controller
        print("brain_bit_controller deleted successfully.")
