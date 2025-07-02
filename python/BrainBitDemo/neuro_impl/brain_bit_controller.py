import contextlib
from threading import Thread, Event
from time import sleep, time

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from neurosdk.scanner import Scanner
from neurosdk.sensor import Sensor
from neurosdk.cmn_types import *
from neurosdk.brainbit_sensor import BrainBitSignalData, BrainBitResistData


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, work):
        super().__init__()
        self.work = work

    def run(self):
        self.work()
        self.finished.emit()


class BrainBitController(QObject):
    sensorConnectionState = pyqtSignal(SensorState)

    def __init__(self):
        super().__init__()
        self.__sensor = None
        self.__scanner = Scanner([SensorFamily.LEBrainBit, SensorFamily.LECallibri])
        self.sensorsFounded   = None       # callback: List[SensorInfo] -> None
        self.sensorBattery    = None       # callback: int -> None
        self.resistReceived   = None       # callback: BrainBitResistData -> None
        self.signalReceived   = None       # callback: BrainBitSignalData -> None
        self.thread           = None
        self.worker           = None
        self._stop_event      = Event()

    def start_scan(self):
        if self.__sensor and self.__sensor.state is SensorState.StateInRange:
            self.__sensor.disconnect()
            del self.__sensor
            self.__sensor = None

        def sensors_founded(scanner, sensors):
            if self.sensorsFounded:
                self.sensorsFounded(sensors)

        self.__scanner.sensorsChanged = sensors_founded
        Thread(target=self.__scanner.start, daemon=True).start()

    def stop_scan(self):
        self.__scanner.stop()
        self.__scanner.sensorsChanged = None

    def create_and_connect(self, sensor_info: SensorInfo):
        def device_connection():
            try:
                self.__sensor = self.__scanner.create_sensor(sensor_info)
            except Exception as err:
                print(err)

            if self.__sensor:
                self.__sensor.sensorStateChanged = self.__connection_state_changed
                self.__sensor.batteryChanged     = self.__battery_changed
                self.sensorConnectionState.emit(SensorState.StateInRange)
            else:
                self.sensorConnectionState.emit(SensorState.StateOutOfRange)

        self.thread = QThread()
        self.worker = Worker(device_connection)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def disconnect_sensor(self):
        if self.__sensor:
            self.__sensor.disconnect()

    def __connection_state_changed(self, sensor: Sensor, state: SensorState):
        self.sensorConnectionState.emit(state)

    def __battery_changed(self, sensor: Sensor, battery: int):
        if self.sensorBattery:
            self.sensorBattery(battery)

    def full_info(self):
        """(Optional) implement to fetch and emit any sensor metadata."""
        pass

    def start_resist(self):
        def _on_resist(sensor, resist: BrainBitResistData):
            if self.resistReceived:
                self.resistReceived(resist)

        self.__sensor.resistDataReceived = _on_resist
        self.__execute_command(SensorCommand.StartResist)

    def stop_resist(self):
        self.__execute_command(SensorCommand.StopResist)
        self.__sensor.resistDataReceived = None

    def start_signal(self):
        def _on_signal(sensor, signal: BrainBitSignalData):
            if self.signalReceived:
                self.signalReceived(signal)

        self.__sensor.signalDataReceived = _on_signal
        self.__execute_command(SensorCommand.StartSignal)

    def stop_signal(self):
        self.__execute_command(SensorCommand.StopSignal)
        self.__sensor.signalDataReceived = None

    def start_interleaved(self, burst_secs: float, interval_secs: float):
        """
        Stream EEG continuously, and take short impedance bursts periodically.
        Runs until stop_interleaved() is called.
        """
        if not self.__sensor:
            print("Sensor not connected")
            return

        self._stop_event.clear()

        def interleave_loop():
            # start EEG
            self.__execute_command(SensorCommand.StartSignal)
            while not self._stop_event.is_set():
                sleep(interval_secs)
                # switch to resist
                self.__execute_command(SensorCommand.StopSignal)
                self.__execute_command(SensorCommand.StartResist)
                sleep(burst_secs)
                self.__execute_command(SensorCommand.StopResist)
                # back to signal
                self.__execute_command(SensorCommand.StartSignal)

            # cleanup once stopped
            self.__execute_command(SensorCommand.StopSignal)

        Thread(target=interleave_loop, daemon=True).start()

    def stop_interleaved(self):
        """Signal to stop the interleaving loop."""
        self._stop_event.set()

    def __execute_command(self, command: SensorCommand):
        def _exec():
            try:
                self.__sensor.exec_command(command)
            except Exception as err:
                print(err)

        Thread(target=_exec, daemon=True).start()

    def __del__(self):
        with contextlib.suppress(Exception):
            self.__sensor.disconnect()
            del self.__sensor


# Instantiate once (or as needed)
brain_bit_controller = BrainBitController()