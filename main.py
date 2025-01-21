from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import (
    QLabel, QColorDialog, QToolBar, QFileDialog, QLineEdit, 
    QApplication)
from PySide6.QtGui import (
    QAction, QIcon, QPixmap, QImage, QShortcut, QKeySequence)
from PySide6.QtCore import Qt, QSize, QByteArray, QSettings

from canvas import Canvas
from dialogs import CanvasSizeDialog, PreferencesDialog

class NightPainterWindow(QtWidgets.QMainWindow):
    def __init__(self): # TODO: make init more functional
        super().__init__()

        self.setWindowTitle("Night Painter")

        # Get primary screen info & open app on primary screen
        self.primaryScreen = QApplication.primaryScreen()
        self.setScreen(self.primaryScreen)
        self.setMinimumSize(320, 180) # Avoid making window too small for use

        # Read config settings 
        self.readSettings()

        # Create canvas 
        self.createCanvas()

        # Color picker dialog
        self.color_picker = QColorDialog(self)

        # File dialog
        self.file_dialog = QFileDialog(self)
        self.file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        self.current_filename = None

        # Color pixmaps
        self.primary_pixmap = QPixmap(16, 16)
        self.primary_pixmap.fill(self.primary_color)
        self.secondary_pixmap = QPixmap(16, 16)
        self.secondary_pixmap.fill(self.secondary_color)

        # Create actions
        self.createActions()

        # Create menu and toolbar
        self.createMenuAndToolbar()

        # Hotkeys
        self.create_hotkeys()

        self.setCentralWidget(self.canvas)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def set_antialiasing(self, aa):
        """ Set antialiasing """
        self.aa = aa
        self.canvas.set_antialiasing(aa)

    def on_paste_click(self):
        """ Paste image from clipboard """
        clipboard = QApplication.clipboard()
        image = clipboard.image()

        if image:
            self.canvas.open_image(image)

    def on_copy_click(self):
        """ Copy pixmap to clipboard as image """
        clipboard = QApplication.clipboard()
        pixmap = self.canvas.pixmap()
        # using clipboard.setPixmap() seems to give bug
        clipboard.setImage(pixmap.toImage())

    def on_preferences_click(self):
        """ Open preferences dialog """
        preferences_dlg = PreferencesDialog(self)
        accepted = preferences_dlg.exec()

    def on_resize_canvas_click(self):
        """ Dialog to resize canvas """
        canvas_size_dlg = CanvasSizeDialog(self)
        canvas_size_dlg.set_width_text(self.canvas.get_width())
        canvas_size_dlg.set_height_text(self.canvas.get_height())
        accepted = canvas_size_dlg.exec()

        if accepted:
            self.canvas.resize_canvas(
                canvas_size_dlg.get_width_int(), 
                canvas_size_dlg.get_height_int())

    def on_new_canvas_click(self):
        """ Create new canvas """
        self.canvas.reset(self.bg_color)
        self.current_filename = None

    def on_open_click(self):
        """
        Open image from file, converting to pixmap and 
        displaying on canvas.
        """
        self.file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog_success = self.file_dialog.exec()

        if file_dialog_success:
            filename = self.file_dialog.selectedFiles()[0]
            self.canvas.open_image(QImage(filename))
            self.current_filename = filename

    def on_save_click(self):
        """ 
        Autosave to file currently associated with canvas,
        or default to manual save if file not yet created 
        """
        if self.current_filename:
            self.canvas.pixmap().save(self.current_filename)
        else:
            self.on_save_as_click()

    def on_save_as_click(self):
        """ Save and associated canvas to specific file """
        self.file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog_success = self.file_dialog.exec()
        
        if file_dialog_success:
            filename = self.file_dialog.selectedFiles()[0]
            self.canvas.pixmap().save(filename)
            self.current_filename = filename

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
        """ Disconnects in-use signals for the color picker """
        self.color_picker.currentColorChanged.disconnect()
        self.color_picker.colorSelected.disconnect()
        self.color_picker.rejected.disconnect()

    def on_pen_size_change(self):
        """ 
        Set pen size according to size input in line edit,
        otherwise revert text in edit box to previous size.
        """
        text = self.pen_size_edit.text()
        prev_pen_size = self.canvas.get_pen_size()
        
        if text == '' or text is None:
            self.pen_size_edit.setText(str(prev_pen_size))
        elif int(text) == 0:
            self.pen_size_edit.setText(str(prev_pen_size))
        else:
            self.canvas.set_pen_size(int(text))

    def create_hotkeys(self):
        """ Create hotkeys """
        # Undo
        undo_hotkey = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Undo),
            self)
        undo_hotkey.activated.connect(self.canvas.undo)
        # Save
        save_hotkey = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Save),
            self)
        save_hotkey.activated.connect(self.on_save_click)
        # Save As
        save_as_hotkey = QShortcut(
            QKeySequence(QKeySequence.StandardKey.SaveAs),
            self)
        save_as_hotkey.activated.connect(self.on_save_as_click)
        # Copy
        copy_hotkey = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Copy),
            self)
        copy_hotkey.activated.connect(self.on_copy_click)
        # Paste
        paste_hotkey = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Paste),
            self)
        paste_hotkey.activated.connect(self.on_paste_click)

    def writeSettings(self):
        """ Write out settings/config """
        settings = QSettings("NightJay", "Night Painter")
        # Main window settings group
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.endGroup()
        # Canvas settings group
        settings.beginGroup("Canvas")
        # TODO: convert color config to HEX values (makes it editable in config)
        settings.setValue("canvas_width", self.canvas.get_width())
        settings.setValue("canvas_height", self.canvas.get_height())
        settings.setValue("primary_color", self.canvas.get_primary_color()) 
        settings.setValue("secondary_color", self.canvas.get_secondary_color())
        settings.setValue("background_color", self.bg_color)
        settings.setValue("pen_size", self.canvas.get_pen_size())
        settings.setValue("antialiasing", self.aa)
        settings.endGroup()

    def readSettings(self):
        """ Read in settings/config """
        settings = QSettings("NightJay", "Night Painter")
        # Main window settings group
        settings.beginGroup("MainWindow")
        geometry = settings.value("geometry", QByteArray())
        if geometry.isEmpty():
            self.resize(
                self.primaryScreen.availableSize().width()//2,
                self.primaryScreen.availableSize().height()//2)
        else:
            self.restoreGeometry(geometry)
        settings.endGroup()
        # Canvas settings group
        settings.beginGroup("Canvas")
        self.canvas_width = int(settings.value("canvas_width", 1280))
        self.canvas_height = int(settings.value("canvas_height", 720))
        self.primary_color = settings.value("primary_color", QtGui.QColor('white'))
        self.secondary_color = settings.value("secondary_color", QtGui.QColor('black'))
        self.bg_color = settings.value("background_color", '#000000')
        self.init_pen_size = int(settings.value("pen_size", 5))
        self.aa = settings.value("antialiasing", True, type=bool)
        settings.endGroup()

    def createCanvas(self):
        """ Create canvas """
        self.canvas = Canvas(
            self.canvas_width, self.canvas_height, self.bg_color, self.aa)
        self.canvas.set_primary_color(self.primary_color)
        self.canvas.set_secondary_color(self.secondary_color)
        self.canvas.set_pen_size(self.init_pen_size)
        self.canvas.setAlignment(Qt.AlignLeft|Qt.AlignTop)

    def createActions(self):
        """ Create actions """
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

        self.action_open = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen), "&Open", self)
        self.action_open.setStatusTip("Open Image from File")
        self.action_open.triggered.connect(self.on_open_click)

        self.action_primary_color = QAction(
            QIcon(self.primary_pixmap),"Primary Color", self)
        self.action_primary_color.setStatusTip("Choose Primary Color")
        self.action_primary_color.triggered.connect(
            self.on_primary_color_click)

        self.action_secondary_color = QAction(
            QIcon(self.secondary_pixmap),"Secondary Color", self)
        self.action_secondary_color.setStatusTip("Choose Secondary Color")
        self.action_secondary_color.triggered.connect(
            self.on_secondary_color_click)
        
        self.action_copy = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.EditCopy), "&Copy", self)
        self.action_copy.setStatusTip("Copy Canvas to Clipboard as Image")
        self.action_copy.triggered.connect(self.on_copy_click)

        self.action_paste = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.EditPaste), "&Paste", self)
        self.action_paste.setStatusTip("Paste Image from Clipboard")
        self.action_paste.triggered.connect(self.on_paste_click)
        
        self.action_resize_canvas = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.ViewFullscreen), 
            "&Resize Canvas", self)
        self.action_resize_canvas.setStatusTip("Resize Canvas")
        self.action_resize_canvas.triggered.connect(
            self.on_resize_canvas_click)

        self.action_open_preferences = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties), 
            "Preference&s", self)
        self.action_open_preferences.setStatusTip("Open Settings Window")
        self.action_open_preferences.triggered.connect(
            self.on_preferences_click)
        
    def createMenuAndToolbar(self):
        """ Create menu and toolbar """
        # Widgets
        pen_size_label = QLabel("Size:")
        pen_size_px_label = QLabel("px")
        self.pen_size_edit = QLineEdit(self)
        self.pen_size_edit.setMaximumWidth(32)
        self.pen_size_edit.setMaxLength(3)
        self.pen_size_edit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.pen_size_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.pen_size_edit.setText(str(self.canvas.get_pen_size()))
        self.pen_size_edit.setInputMask('000')
        self.pen_size_edit.editingFinished.connect(self.on_pen_size_change)

        # Menus
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.action_new_canvas)
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        file_menu.addAction(self.action_open)

        edit_menu = menu.addMenu("&Edit")
        edit_menu.addAction(self.action_copy)
        edit_menu.addAction(self.action_paste)
        edit_menu.addAction(self.action_resize_canvas)
        edit_menu.addAction(self.action_open_preferences)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addAction(self.action_copy)
        self.toolbar.addAction(self.action_paste)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(pen_size_label)
        self.toolbar.addWidget(self.pen_size_edit)
        self.toolbar.addWidget(pen_size_px_label)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_primary_color)
        self.toolbar.addAction(self.action_secondary_color)

    def closeEvent(self, e):
        """ On close, write config settings """
        self.writeSettings()
        return super().closeEvent(e)


if __name__ == "__main__":
    # Run app
    app = QApplication([])
    window = NightPainterWindow()
    window.show()
    app.exec()