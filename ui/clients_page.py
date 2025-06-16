from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QHBoxLayout, QCheckBox
)
import models.client as Client


class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.all_clients = []  # Para mantener todos los clientes y poder filtrar
        self.filtered_clients = []

        layout = QVBoxLayout()

        # Total de clientes
        self.total_label = QLabel("Total de clientes: 0")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.total_label)

        # Sección de búsqueda y filtros
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o apellido...")
        self.search_input.textChanged.connect(self.apply_filters)

        self.email_checkbox = QCheckBox("Con email")
        self.email_checkbox.stateChanged.connect(self.apply_filters)

        self.phone_checkbox = QCheckBox("Con celular")
        self.phone_checkbox.stateChanged.connect(self.apply_filters)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.email_checkbox)
        filter_layout.addWidget(self.phone_checkbox)

        layout.addLayout(filter_layout)

        # Lista de clientes
        self.client_list = QListWidget()
        layout.addWidget(self.client_list)

        self.setLayout(layout)

    def load_clients(self):
        """
        clients: lista de dicts con claves 'nombre', 'apellido', 'email' (opcional), 'celular' (opcional)
        """
        self.all_clients = clients = Client.get_all()
        self.total_label.setText(f"Total de clientes: {len(clients)}")
        self.apply_filters()

    def apply_filters(self):
        text = self.search_input.text().lower()
        only_with_email = self.email_checkbox.isChecked()
        only_with_phone = self.phone_checkbox.isChecked()

        self.client_list.clear()
        self.filtered_clients = []

        for client in self.all_clients:
            full_name = f"{client['nombre']} {client['apellido']}".lower()
            if text and text not in full_name:
                continue
            if only_with_email and not client.get("email"):
                continue
            if only_with_phone and not client.get("celular"):
                continue

            item_text = f"{client['nombre']} {client['apellido']}"
            if client.get("email"):
                item_text += f" | Email: {client['email']}"
            if client.get("celular"):
                item_text += f" | Celular: {client['celular']}"

            self.filtered_clients.append(client)
            self.client_list.addItem(QListWidgetItem(item_text))