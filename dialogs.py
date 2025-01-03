from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit)

class CanvasSizeDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Canvas Size Editor")

        # Buttons
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout
        px_label1 = QLabel("px")
        px_label2 = QLabel("px")

        width_layout = QHBoxLayout()
        width_label = QLabel("Width: ")
        width_edit = QLineEdit()
        width_layout.addWidget(width_label)
        width_layout.addWidget(width_edit)
        width_layout.addWidget(px_label1)

        height_layout = QHBoxLayout()
        height_label = QLabel("Height:")
        height_edit = QLineEdit()
        height_layout.addWidget(height_label)
        height_layout.addWidget(height_edit)
        height_layout.addWidget(px_label2)

        layout = QVBoxLayout()
        layout.addLayout(width_layout)
        layout.addLayout(height_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

