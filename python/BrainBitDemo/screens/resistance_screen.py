
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMainWindow


class ResistanceScreen(QMainWindow):
    normal_resist_border = 2_000_000

    def __init__(self,brain_bit_controller,stack_navigation, history_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brain_bit_controller = brain_bit_controller    
        self.stack_navigation = stack_navigation
        self.history_stack = history_stack
        
        loadUi("ui/ResistanceScreenUI.ui", self)
        self.resistButton.setText('Start')
        self.backButton.clicked.connect(self.__close_screen)
        self.resistButton.clicked.connect(self.__resist_button_clicked)
        self.brain_bit_controller.resistReceived = self.resist_received

        self.__is_started = False

    def __resist_button_clicked(self):
        if self.__is_started:
            self.__stop_resist()
        else:
            self.__start_resist()

    def __start_resist(self):
        self.resistButton.setText('Stop')
        self.brain_bit_controller.resistReceived = self.resist_received
        self.brain_bit_controller.start_resist()
        self.__is_started = True

    def __stop_resist(self):
        self.resistButton.setText('Start')
        self.brain_bit_controller.stop_resist()
        self.brain_bit_controller.resistReceived = None
        self.__is_started = False

    def resist_received(self, resist):
        self.o1Value.setText(str(resist.O1))
        self.o1Q.setText('Good' if resist.O1 != float('inf') and resist.O1 > self.normal_resist_border else 'Poor')
        self.o2Value.setText(str(resist.O2))
        self.o2Q.setText('Good' if resist.O2 != float('inf') and resist.O2 > self.normal_resist_border else 'Poor')
        self.t3Value.setText(str(resist.T3))
        self.t3Q.setText('Good' if resist.T3 != float('inf') and resist.T3 > self.normal_resist_border else 'Poor')
        self.t4Value.setText(str(resist.T4))
        self.t4Q.setText('Good' if resist.T4 != float('inf') and resist.T4 > self.normal_resist_border else 'Poor')

    def __close_screen(self):
        self.__stop_resist()
        if self.history_stack:
            previous_screen = self.history_stack.pop()  # Get the last visited screen
            self.stack_navigation.setCurrentWidget(previous_screen)