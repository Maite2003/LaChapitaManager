from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class SuppliersPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Página de proveedores"))
        self.setLayout(layout)