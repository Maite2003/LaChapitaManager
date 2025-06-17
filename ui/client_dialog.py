from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QDialog, QLabel, QHBoxLayout, QPushButton, QMessageBox

class ClientDialog(QDialog):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.client = client
        if self.client:
            self.setWindowTitle("Editar cliente")
            self.name_input = QLineEdit(client.get('name', ''))
            self.surname_input = QLineEdit(client.get('surname', ''))
            self.phone_input = QLineEdit(client.get('phone', '') or '')
            self.mail_input = QLineEdit(client.get('mail', '') or '')
        else:
            self.setWindowTitle("Crear nuevo cliente")
            self.name_input = QLineEdit()
            self.surname_input = QLineEdit()
            self.phone_input = QLineEdit()
            self.mail_input = QLineEdit()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Apellido:"))
        layout.addWidget(self.surname_input)
        layout.addWidget(QLabel("Teléfono:"))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.mail_input)

        # Botones aceptar/cancelar
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_cancel = QPushButton("Cancelar")
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "surname": self.surname_input.text().strip(),
            "phone": self.phone_input.text().strip() or None,
            "mail": self.mail_input.text().strip() or None
        }