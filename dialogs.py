from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit)

class CanvasSizeDialog(QDialog):
    """
    Dialog to edit the canvas size.

    parent -- Parent QWidget 
    """
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Canvas Size Editor")

        # Useful variables
        edit_max_len = 4
        edit_input_mask = '0000'
        self.default_size = 8 # default for invalid input

        # Buttons
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout
        px_label1 = QLabel("px")
        px_label2 = QLabel("px")

        self.width_edit = QLineEdit()
        self.height_edit = QLineEdit()
        self.width_edit.setMaxLength(edit_max_len)
        self.height_edit.setMaxLength(edit_max_len)
        self.width_edit.setInputMask(edit_input_mask)
        self.height_edit.setInputMask(edit_input_mask)

        width_layout = QHBoxLayout()
        width_label = QLabel("Width: ")
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_edit)
        width_layout.addWidget(px_label1)

        height_layout = QHBoxLayout()
        height_label = QLabel("Height:")
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_edit)
        height_layout.addWidget(px_label2)

        layout = QVBoxLayout()
        layout.addLayout(width_layout)
        layout.addLayout(height_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def set_width_text(self, s:str):
        """ Set text of 'width' line edit by string """
        self.width_edit.setText(s)

    def set_width_text(self, num:int):
        """ Set text of 'width' line edit by int '"""
        self.width_edit.setText(str(num))

    def set_height_text(self, s:str):
        """ Set text of 'height' line edit by string """
        self.height_edit.setText(s)

    def set_height_text(self, num:int):
        """ Set text of 'height' line edit by int """
        self.height_edit.setText(str(num))

    def get_width_text(self) -> str:
        """ Return 'width' line edit's text """
        return self.width_edit.text()
    
    def get_height_text(self) -> str:
        """ Return 'height' line edit's text """
        return self.height_edit.text()
    
    def get_width_int(self) -> int:
        """ 
        Return 'width' line edit's text as int,
        returning default size if input invalid.
        """
        width = int(self.width_edit.text())
        if width > 0:
            return width
        else:
            return self.default_size
    
    def get_height_int(self) -> int:
        """ 
        Return 'height' line edit's text as int,
        returning default size if input invalid.
        """
        height = int(self.height_edit.text())
        if height > 0:
            return height
        else:
            return self.default_size


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        