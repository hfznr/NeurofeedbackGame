from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QPen


class CovertWidget(QWidget):
    def __init__(self, frequency=1.7, flicker_area_percentage=0.25,flicker_area_location = "m", parent=None):
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
        self.flicker_area_location = flicker_area_location
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
        
    def update_flicker_area_left(self,width, height, flicker_width, flicker_height):
        # Center the flickering area in the middle of the window
        self.flicker_area = QRect(
            (flicker_width - flicker_width ) ,  # Centered horizontally (width - flicker_width) // 2 #put left bottom center (width* 1 // 4 - flicker_width // 2 ) 
            (height - flicker_height ),  # Centered vertically (height - flicker_height) // 2 (height * 3 // 4 - flicker_height // 2)
            flicker_width,
            flicker_height
        )
        
    
    def update_flicker_area_mid(self,width, height, flicker_width, flicker_height):
        # Center the flickering area in the middle of the window
        self.flicker_area = QRect(
            (width - flicker_width) // 2,
            (height - flicker_height) // 2,
            flicker_width,
            flicker_height
        )
        
    def update_flicker_area_right(self,width, height, flicker_width, flicker_height):  
        # Center the flickering area in the middle of the window
        self.flicker_area = QRect(
            (width - flicker_width),  # Centered horizontally (width - flicker_width) // 2
            (height - flicker_height),  # Centered vertically (height - flicker_height) // 2
            flicker_width,
            flicker_height
        )
        
    def update_flicker_area(self):
        """Update the flickering area based on the window size."""
        
        # Get the current window size
        width = self.width()
        height = self.height()

        # Calculate the dimensions of the flickering area based on the percentage
        flicker_width = int(width * self.flicker_area_percentage)
        flicker_height = int(height * self.flicker_area_percentage)
        
        location = self.flicker_area_location
        
        if location == "l":
            self.update_flicker_area_left(width, height, flicker_width, flicker_height)
        elif location == "m":  
            self.update_flicker_area_mid(width, height, flicker_width, flicker_height)
        elif location == "r":
            self.update_flicker_area_right(width, height, flicker_width, flicker_height)
        

    def paintEvent(self, event):
        """Paint the full screen with the current color and a centered red cross."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(64, 64, 64))

        # Set background color (flickering between black and white)
        
        bg_color = QColor(64, 64, 64) if self.is_black else QColor(100, 100, 100)
        #bg_color = QColor(0, 0, 0) if self.is_black else QColor(255, 255, 255)
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


