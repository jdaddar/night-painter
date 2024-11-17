from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QLabel, QColorDialog, QToolBar
from PySide6.QtGui import QScreen, QGuiApplication, QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize, QPoint

from canvas import Canvas

class NightPainterWindow(QtWidgets.QMainWindow):
    def __init__(self): # TODO: make init more functional
        super().__init__()

        self.setWindowTitle("Night Painter")

        # TODO: fix all this to use settings to maintain previous sizes
        # Get primary screen info & open app on primary screen
        self.primaryScreen = QGuiApplication.primaryScreen()
        self.setScreen(self.primaryScreen)
        # Set initial window size based on screen size
        initial_size_divider = 2
        primary_screen_size = (self.primaryScreen.availableSize().width(), 
                               self.primaryScreen.availableSize().height())
        initial_width = (primary_screen_size[0]//initial_size_divider)
        initial_height = (primary_screen_size[1]//initial_size_divider)
        self.resize(initial_width, initial_height)
        self.setMinimumSize(320, 180) # Avoid making window too small for use

        # Create canvas 
        self.canvas = Canvas(initial_width, initial_height)
        self.canvas.setAlignment(Qt.AlignLeft|Qt.AlignTop)

        # Color picker
        self.color_picker = QColorDialog(self)
        self.color_picker.colorSelected.connect(
            lambda x: self.color_picker.currentColorChanged.disconnect())

        # Color pixmaps
        self.primary_color = self.canvas.get_primary_color()
        self.secondary_color = self.canvas.get_secondary_color()
        self.primary_pixmap = QPixmap(32, 32)
        self.primary_pixmap.fill(self.primary_color)
        self.secondary_pixmap = QPixmap(32, 32)
        self.secondary_pixmap.fill(self.secondary_color)

        # Actions
        self.action_save_as = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.DocumentSaveAs), "&Save As", self)
        self.action_save_as.setStatusTip("Save File to PC")
        self.action_save_as.triggered.connect(self.on_save_as_click)

        self.action_primary_color = QAction(
            QIcon(self.primary_pixmap),"Primary Color", self)
        self.action_primary_color.setStatusTip("Choose Primary Color")
        self.action_primary_color.triggered.connect(self.on_primary_color_click)

        self.action_secondary_color = QAction(
            QIcon(self.secondary_pixmap),"Secondary Color", self)
        self.action_secondary_color.setStatusTip("Choose Secondary Color")
        self.action_secondary_color.triggered.connect(self.on_secondary_color_click)

        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.action_save_as)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addAction(self.action_primary_color)
        self.toolbar.addAction(self.action_secondary_color)

        self.setCentralWidget(self.canvas)

    def keyPressEvent(self, e:QtGui.QKeyEvent):
        # 'Undo' hotkey
        undo_hotkey = Qt.KeyboardModifier.ControlModifier|Qt.Key.Key_Z
        if e.keyCombination() == undo_hotkey:
            self.canvas.undo()

    def on_save_as_click(self):
        """ Save canvas to file """
        pass

    def on_primary_color_click(self):
        """ Open color picker to change primary color """
        # TODO : change how this works to use QColorDialog.open properly
        self.color_picker.setCurrentColor(self.primary_color)
        self.color_picker.currentColorChanged.connect(
            self.change_primary_color)
        self.color_picker.open()

    def change_primary_color(self):
        """ Dynamically primary color based on color picker choice """
        self.primary_color = self.color_picker.currentColor()
        self.primary_pixmap.fill(self.primary_color)
        self.action_primary_color.setIcon(self.primary_pixmap)
        self.canvas.set_primary_color(self.primary_color)

    def on_secondary_color_click(self):
        """ Open color picker to change secondary color """
        # TODO : change how this works to use QColorDialog.open properly
        self.color_picker.setCurrentColor(self.secondary_color)
        self.color_picker.currentColorChanged.connect(
            self.change_secondary_color)
        self.color_picker.open()

    def change_secondary_color(self):
        """ Dynamically secondary color based on color picker choice """
        self.secondary_color = self.color_picker.currentColor()
        self.secondary_pixmap.fill(self.secondary_color)
        self.action_secondary_color.setIcon(self.secondary_pixmap)
        self.canvas.set_secondary_color(self.secondary_color)


# Run app
app = QtWidgets.QApplication([])
window = NightPainterWindow()
window.show()
app.exec()