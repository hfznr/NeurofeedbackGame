
from ui.plots import SignalPlot
from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi


class SignalScreen(QMainWindow):
    def __init__(self,brain_bit_controller,stack_navigation, history_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/SignalScreenUI.ui", self)
        self.brain_bit_controller = brain_bit_controller
        self.stack_navigation = stack_navigation
        self.history_stack = history_stack
        
        self.backButton.clicked.connect(self.__close_screen)
        self.signalButton.clicked.connect(self.__start_button_clicked)
        
        self.o1Graph = SignalPlot()
        self.o2Graph = SignalPlot()
        self.t3Graph = SignalPlot()
        self.t4Graph = SignalPlot()
        self.signalScreenLayout.addWidget(self.o1Graph)
        self.signalScreenLayout.addWidget(self.o2Graph)
        self.signalScreenLayout.addWidget(self.t3Graph)
        self.signalScreenLayout.addWidget(self.t4Graph)

        self.__is_started = False

    def __start_button_clicked(self):
        if self.__is_started:
            self.__stop_signal()
        else:
            self.__start_signal()

    def signal_received(self, signal):
        o1Samples = [sample.O1 for sample in signal]
        o2Samples = [sample.O2 for sample in signal]
        t3Samples = [sample.T3 for sample in signal]
        t4Samples = [sample.T4 for sample in signal]
        self.o1Graph.update_data(o1Samples)
        self.o2Graph.update_data(o2Samples)
        self.t3Graph.update_data(t3Samples)
        self.t4Graph.update_data(t4Samples)

    def __start_signal(self):
        self.signalButton.setText('Stop')
        self.o1Graph.start_draw()
        self.o2Graph.start_draw()
        self.t3Graph.start_draw()
        self.t4Graph.start_draw()
        self.brain_bit_controller.signalReceived = self.signal_received
        self.brain_bit_controller.start_signal()
        self.__is_started = True

    def __stop_signal(self):
        self.signalButton.setText('Start')
        self.o1Graph.stop_draw()
        self.o2Graph.stop_draw()
        self.t3Graph.stop_draw()
        self.t4Graph.stop_draw()
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.resistReceived = None
        self.__is_started = False

    def __close_screen(self):
        self.__stop_signal()
        if self.history_stack:
            previous_screen = self.history_stack.pop()  # Get the last visited screen
            self.stack_navigation.setCurrentWidget(previous_screen)
