from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QLabel, QColorDialog, QToolBar
from PySide6.QtGui import QScreen, QGuiApplication, QAction, QIcon, QPixmap
from PySide6.QtCore import Qt, QSize, QPoint, QByteArray, QBuffer

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

        # Color pixmaps
        self.primary_color = self.canvas.get_primary_color()
        self.secondary_color = self.canvas.get_secondary_color()
        self.primary_pixmap = QPixmap(32, 32)
        self.primary_pixmap.fill(self.primary_color)
        self.secondary_pixmap = QPixmap(32, 32)
        self.secondary_pixmap.fill(self.secondary_color)

        # Actions
        self.action_new_canvas = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew), "&New", self)
        self.action_new_canvas.setStatusTip("Create New Canvas")
        self.action_new_canvas.triggered.connect(self.on_new_canvas_click)

        self.action_save = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), "&Save", self)
        self.action_save.setStatusTip("Quicksave File")
        self.action_save.triggered.connect(self.on_save_click)

        self.action_save_as = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.DocumentSaveAs), "Save &As", self)
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
        file_menu.addAction(self.action_new_canvas)
        file_menu.addAction(self.action_save)
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

        # 'Save' hotkey
        save_hotkey = Qt.KeyboardModifier.ControlModifier|Qt.Key.Key_S
        if e.keyCombination() == save_hotkey or e.key == Qt.Key.Key_Save:
            self.on_save_click()

    def on_new_canvas_click(self):
        """ Create new canvas """
        self.canvas.reset()

    def on_save_click(self):
        # TODO: make user choose filename/path if canvas not yet saved
        #       otherwise save automatically over previous filename
        self.canvas.pixmap().save("image.png", 'PNG')

    def on_save_as_click(self):
        """ Save canvas to file """
        pass

    def on_primary_color_click(self):
        """ Open color picker to change primary color """
        self.color_picker.setCurrentColor(self.primary_color)
        self.color_picker.currentColorChanged.connect(
            self.change_primary_color)
        self.color_picker.colorSelected.connect(
            self.selected_primary_color)
        self.color_picker.rejected.connect(
            self.cancel_primary_color)
        self.color_picker.open()

    def change_primary_color(self):
        """ Dynamically primary color based on color picker choice """
        self.primary_pixmap.fill(self.color_picker.currentColor())
        self.action_primary_color.setIcon(self.primary_pixmap)

    def selected_primary_color(self):
        """ Change primary color, send to canvas, disconnect signals """
        new_color = self.color_picker.currentColor()
        self.primary_color = new_color
        self.canvas.set_primary_color(new_color)
        # Disconnect
        self.disconnect_color_picker_signals()

    def cancel_primary_color(self):
        """ 
        Cancel primary color selection, revert icon, disconnect signals 
        """
        self.primary_pixmap.fill(self.primary_color)
        self.action_primary_color.setIcon(self.primary_pixmap)
        # Disconnect
        self.disconnect_color_picker_signals()

    def on_secondary_color_click(self):
        """ Open color picker to change secondary color """
        self.color_picker.setCurrentColor(self.secondary_color)
        self.color_picker.currentColorChanged.connect(
            self.change_secondary_color)
        self.color_picker.colorSelected.connect(
            self.selected_secondary_color)
        self.color_picker.rejected.connect(
            self.cancel_secondary_color)
        self.color_picker.open()

    def change_secondary_color(self):
        """ Dynamically secondary color based on color picker choice """
        self.secondary_pixmap.fill(self.color_picker.currentColor())
        self.action_secondary_color.setIcon(self.secondary_pixmap)

    def selected_secondary_color(self):
        """ Change secondary color, send to canvas, disconnect signals """
        new_color = self.color_picker.currentColor()
        self.secondary_color = new_color
        self.canvas.set_secondary_color(new_color)
        # Disconnect
        self.disconnect_color_picker_signals()

    def cancel_secondary_color(self):
        """ 
        Cancel secondary color selection, revert icon, disconnect signals 
        """
        self.secondary_pixmap.fill(self.secondary_color)
        self.action_secondary_color.setIcon(self.secondary_pixmap)
        # Disconnect
        self.disconnect_color_picker_signals()

    def disconnect_color_picker_signals(self):
        self.color_picker.currentColorChanged.disconnect()
        self.color_picker.colorSelected.disconnect()
        self.color_picker.rejected.disconnect()


# Run app
app = QtWidgets.QApplication([])
window = NightPainterWindow()
window.show()
app.exec()