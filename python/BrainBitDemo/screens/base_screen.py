from PyQt6.QtWidgets import QMainWindow
import logging

logging.basicConfig(level=logging.INFO)


class BaseScreen(QMainWindow):
    def closeEvent(self, event):
        logging.info("Application is closing. Disconnecting sensor...")
        try:
            brain_bit_controller.disconnect_sensor()
            del brain_bit_controller
            logging.info("Sensor disconnected successfully.")
        except Exception as e:
            logging.error(f"Error during disconnection: {e}")
        event.accept()
