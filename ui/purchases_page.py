from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Página de Compras"))
        self.setLayout(layout)