from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QScreen, QGuiApplication
from PySide6.QtCore import Qt

from canvas import Canvas

class NightPainterWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Night Painter")

        # TODO: fix all this to use settings to maintain previous sizes
        # Get primary screen info & open app on primary screen
        self.primaryScreen = QGuiApplication.primaryScreen()
        self.setScreen(self.primaryScreen)
        # Set initial window size based on screen size
        initial_size_divider = 2
        initial_width = self.primaryScreen.availableSize().width()//initial_size_divider
        initial_height = self.primaryScreen.availableSize().height()//initial_size_divider
        self.resize(initial_width, initial_height)
        self.setMinimumSize(320, 180) # Avoid making window too small for use

        # Create canvas 
        self.canvas = Canvas(initial_width, initial_height)
        self.canvas.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(self.canvas)

app = QtWidgets.QApplication([])
window = NightPainterWindow()
window.show()
app.exec()