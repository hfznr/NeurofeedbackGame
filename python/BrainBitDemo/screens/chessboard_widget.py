from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QBrush


class ChessboardWidget(QWidget):
    def __init__(self, rows=8, cols=8, frequency=1.7, parent=None):
        """
        Initializes the Chessboard widget.

        :param rows: Number of rows in the chessboard.
        :param cols: Number of columns in the chessboard.
        :param frequency: Flickering frequency in Hz.
        :param parent: Parent widget.
        """
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.frequency = frequency
        self.tile_width = self.width() // self.cols
        self.tile_height = self.height() // self.rows
        self.white_on = True
        self.timer = QTimer(self)
        self.timer.setInterval(int(1000 / (2 * self.frequency)))  # Convert frequency to milliseconds
        self.timer.timeout.connect(self.toggle_color)

    def start_flickering(self):
        """Start the flickering effect."""
        self.timer.start()

    def stop_flickering(self):
        """Stop the flickering effect."""
        self.timer.stop()

    def set_frequency(self, frequency):
        """Set the flickering frequency."""
        self.frequency = frequency
        self.timer.setInterval(int(1000 / (2 * self.frequency)))

    def toggle_color(self):
        """Toggle the color state for flickering."""
        self.white_on = not self.white_on
        self.update()  # Trigger a repaint

    def resizeEvent(self, event):
        """Handle resizing to recalculate tile sizes."""
        self.tile_width = self.width() // self.cols
        self.tile_height = self.height() // self.rows
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Draw the chessboard."""
        painter = QPainter(self)
        color1 = QColor(255, 255, 255) if self.white_on else QColor(0, 0, 0)
        color2 = QColor(0, 0, 0) if self.white_on else QColor(255, 255, 255)

        for row in range(self.rows):
            for col in range(self.cols):
                tile_color = color1 if (row + col) % 2 == 0 else color2
                painter.setBrush(QBrush(tile_color, Qt.BrushStyle.SolidPattern))
                painter.drawRect(
                    col * self.tile_width,
                    row * self.tile_height,
                    self.tile_width,
                    self.tile_height
                )

        # Draw the red cross in the center (non-flickering)
        cross_color = QColor(255, 0, 0)  # Define the red color
        pen = painter.pen()
        cross_thickness = 12  # Thicker lines
        pen.setColor(cross_color)
        pen.setWidth(cross_thickness)
        painter.setPen(pen)

        cross_length = self.tile_width // 4
        middle_x = self.width() // 2
        middle_y = self.height() // 2

        # Draw the rotated cross
        painter.drawLine(
            middle_x - cross_length // 2, middle_y - cross_length // 2,
            middle_x + cross_length // 2, middle_y + cross_length // 2
        )
        painter.drawLine(
            middle_x - cross_length // 2, middle_y + cross_length // 2,
            middle_x + cross_length // 2, middle_y - cross_length // 2
        )
