import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget


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

app = QApplication(sys.argv)
stackNavigation = QStackedWidget()

history_stack = []  # Stack to maintain the navigation history

searchScreen = SearchScreen(brain_bit_controller,stackNavigation, history_stack)
resistScreen = ResistanceScreen(brain_bit_controller,stackNavigation, history_stack)
signalScreen = SignalScreen(brain_bit_controller,stackNavigation, history_stack)
emotionBipolarScreen = EmotionBipolarScreen(brain_bit_controller,stackNavigation, history_stack)
emotionMonopolarScreen = EmotionMonopolarScreen(brain_bit_controller,stackNavigation, history_stack)
spectrumScreen = SpectrumScreen(brain_bit_controller,stackNavigation, history_stack)
chessboardScreen = ChessboardScreen(brain_bit_controller,stackNavigation, history_stack)
blackWhiteScreen = BlackWhiteScreen(brain_bit_controller,stackNavigation, history_stack)

menuScreen = MenuScreen(brain_bit_controller,stackNavigation, history_stack,
                        searchScreen, 
                        resistScreen, 
                        signalScreen,
                        emotionBipolarScreen, 
                        emotionMonopolarScreen, 
                        spectrumScreen,
                        chessboardScreen,
                        blackWhiteScreen)

stackNavigation.addWidget(menuScreen)
stackNavigation.addWidget(searchScreen)
stackNavigation.addWidget(resistScreen)
stackNavigation.addWidget(signalScreen)
stackNavigation.addWidget(emotionBipolarScreen)
stackNavigation.addWidget(emotionMonopolarScreen)
stackNavigation.addWidget(spectrumScreen)
stackNavigation.addWidget(chessboardScreen)
stackNavigation.addWidget(blackWhiteScreen)


stackNavigation.setCurrentWidget(menuScreen)
stackNavigation.show()

try:
    app.exec()
except Exception as e:
    print(f"Error during application execution: {e}")
finally:
    try:
        print("Stopping signals...")
        brain_bit_controller.stop_signal()
        print("Disconnecting the sensor...")
        brain_bit_controller.disconnect_sensor()
    except Exception as disconnect_error:
        print(f"Error during brain_bit_controller cleanup: {disconnect_error}")
    finally:
        # Ensure the object is deleted regardless of errors
        del brain_bit_controller
        print("brain_bit_controller deleted successfully.")

