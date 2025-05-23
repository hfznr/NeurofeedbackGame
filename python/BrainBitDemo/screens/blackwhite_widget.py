from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt,QRect
from PyQt6.QtGui import QPainter, QColor, QPen


class BlackWhiteWidget(QWidget):
    def __init__(self, frequency=1.7, flicker_area_percentage=0.75, parent=None):
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
        
        self.flicker_area_percentage = flicker_area_percentage
        self.update_flicker_area()
        
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
        
    def update_flicker_area(self):
        """Update the flickering area based on the window size."""
        # Get the current window size
        width = self.width()
        height = self.height()

        # Calculate the dimensions of the flickering area based on the percentage
        flicker_width = int(width * self.flicker_area_percentage)  # Convert to int
        flicker_height = int(height * self.flicker_area_percentage)  # Convert to int

        # Center the flickering area in the middle of the window
        self.flicker_area = QRect(
            (width - flicker_width) // 2,  # Centered horizontally
            (height - flicker_height) // 2,  # Centered vertically
            flicker_width,
            flicker_height
        )

    def paintEvent(self, event):
        """Paint the full screen with the current color and a centered red cross."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        # Set background color (flickering between black and white)
        bg_color = QColor(0, 0, 0) if self.is_black else QColor(255, 255, 255)
        painter.fillRect(self.flicker_area, bg_color)

        # Draw a red cross in the center
        cross_color = QColor(255, 0, 0)  # Red color
        pen = QPen(cross_color, 10)  # Thick red lines
        painter.setPen(pen)

        middle_x = self.rect().width() // 2
        middle_y = self.rect().height() // 2
        cross_length = min(self.rect().width(), self.rect().height()) // 16  # Ensure visibility

        painter.drawLine(
            middle_x - cross_length // 2, middle_y - cross_length // 2,
            middle_x + cross_length // 2, middle_y + cross_length // 2
        )
        painter.drawLine(
            middle_x - cross_length // 2, middle_y + cross_length // 2,
            middle_x + cross_length // 2, middle_y - cross_length // 2
        )
        
    def resizeEvent(self, event):
        """Update the flickering area when the window is resized."""
        self.update_flicker_area()
        super().resizeEvent(event)


