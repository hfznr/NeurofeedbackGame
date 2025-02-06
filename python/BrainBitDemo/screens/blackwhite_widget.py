from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QPen


class BlackWhiteWidget(QWidget):
    def __init__(self, frequency=1.7, parent=None):
        """
        A full-screen black and white flickering widget with a centered red cross.

        :param frequency: Flickering frequency in Hz.
        :param parent: Parent widget.
        """
        super().__init__(parent)
        self.frequency = frequency
        self.is_black = True  # Initial color state
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_color)
        # Ensure flickering starts automatically

    def start_flickering(self):
        """Start the flickering effect."""
        if self.frequency > 0:
            self.timer.start(int(1000 / self.frequency))  # Convert Hz to milliseconds

    def stop_flickering(self):
        """Stop the flickering effect."""
        self.timer.stop()
        self.is_black = True  # Default to black when stopped
        self.repaint()  # Ensure repaint happens immediately

    def set_frequency(self, frequency):
        """Set the flickering frequency."""
        if frequency > 0:
            self.frequency = frequency
            self.timer.setInterval(int(1000 / self.frequency))
        else:
            self.stop_flickering()

    def toggle_color(self):
        """Switch between black and white background."""
        self.is_black = not self.is_black
        self.repaint()  # Force immediate repaint

    def paintEvent(self, event):
        """Paint the full screen with the current color and a centered red cross."""
        painter = QPainter(self)

        # Set background color (flickering between black and white)
        bg_color = QColor(0, 0, 0) if self.is_black else QColor(255, 255, 255)
        painter.fillRect(self.rect(), bg_color)

        # Draw a red cross in the center
        cross_color = QColor(255, 0, 0)  # Red color
        pen = QPen(cross_color, 10)  # Thick red lines
        painter.setPen(pen)

        middle_x = self.width() // 2
        middle_y = self.height() // 2
        cross_length = min(self.width(), self.height()) // 16  # Ensure visibility

        painter.drawLine(
            middle_x - cross_length // 2, middle_y - cross_length // 2,
            middle_x + cross_length // 2, middle_y + cross_length // 2
        )
        painter.drawLine(
            middle_x - cross_length // 2, middle_y + cross_length // 2,
            middle_x + cross_length // 2, middle_y - cross_length // 2
        )


