
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMainWindow

class SearchScreen(QMainWindow):
    def __init__(self,brain_bit_controller,stack_navigation, history_stack, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/SearchScreenUI.ui", self)
        self.brain_bit_controller = brain_bit_controller
        self.stack_navigation = stack_navigation
        self.history_stack = history_stack
        self.is_searching = False
        self.sensorsList = None
        self.backButton.clicked.connect(self.__close_screen)
        self.searchButton.clicked.connect(self.__search)
        self.listWidget.itemClicked.connect(self.__connect_to_sensor)

    def __search(self):
        if self.is_searching:
            self.__stop_scan()
        else:
            self.__start_scan()

    def __sensors_founded(self, sensors):
        self.sensorsList = sensors
        self.listWidget.clear()
        self.listWidget.addItems([sens.Name + ' (' + sens.SerialNumber + ')' for sens in sensors])

    def __connect_to_sensor(self, item):
        item_number = self.listWidget.row(item)
        self.brain_bit_controller.sensorConnectionState.connect(self.__is_sensor_connected)
        self.brain_bit_controller.create_and_connect(sensor_info=self.sensorsList[item_number])

    def __is_sensor_connected(self, sensor_state):
        self.__close_screen()

    def __start_scan(self):
        self.searchButton.setText('Stop')
        self.brain_bit_controller.sensorsFounded = self.__sensors_founded
        self.brain_bit_controller.start_scan()
        self.is_searching = True

    def __stop_scan(self):
        self.searchButton.setText('Search')
        self.brain_bit_controller.stop_scan()
        self.brain_bit_controller.sensorsFounded = None
        self.is_searching = False

    def __close_screen(self):
        try:
            self.brain_bit_controller.sensorConnectionState.disconnect(self.__is_sensor_connected)
        except Exception as err:
            print(err)
        self.__stop_scan()
        if self.history_stack:
            previous_screen = self.history_stack.pop()  # Get the last visited screen
            self.stack_navigation.setCurrentWidget(previous_screen)