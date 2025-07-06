from PySide6.QtWidgets import QCheckBox, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt

class DriveBackupToggle(QWidget):
    def __init__(self, checked=False, on_toggle=None, parent=None):
        super().__init__(parent)

        self.on_toggle = on_toggle

        self.label = QLabel("Drive Backup")
        self.toggle = QCheckBox()
        self.toggle.setChecked(checked)
        self.toggle.setTristate(False)
        self.toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle.toggled.connect(self.on_toggle)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.toggle)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        self.setLayout(layout)

    def set_checked(self, checked: bool):
        self.toggle.setChecked(checked)