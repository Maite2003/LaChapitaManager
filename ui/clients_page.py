from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QCheckBox, QPushButton, QDialog, QHeaderView, QMessageBox, QComboBox
)
from models.client import Client
from ui.client_dialog import ClientDialog


class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.all_clients = []
        self.filtered_clients = []

        layout = QVBoxLayout()

        # Total de clientes
        self.total_label = QLabel("Total de clientes: 0")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.total_label)

        # Botón para crear cliente
        btn_new_client = QPushButton("Nuevo Cliente")
        btn_new_client.clicked.connect(self.open_client)
        layout.addWidget(btn_new_client)

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

        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Ordenar por nombre (A-Z)",
            "Ordenar por nombre (Z-A)",
            "Ordenar por apellido (A-Z)",
            "Ordenar por apellido (Z-A)"
        ])
        self.sort_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.sort_combo)

        self.btn_delete_selected = QPushButton("Eliminar")
        self.btn_delete_selected.setEnabled(False)  # Inicialmente deshabilitado
        self.btn_delete_selected.clicked.connect(self.delete_selected_clients)
        filter_layout.addWidget(self.btn_delete_selected)


        layout.addLayout(filter_layout)

        # Tabla de clientes
        self.client_table = QTableWidget()
        self.client_table.setColumnCount(5)
        self.client_table.setHorizontalHeaderLabels(["Nombre", "Apellido", "Email", "Celular", "       "])
        self.client_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.client_table)
        self.client_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.client_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.client_table.itemSelectionChanged.connect(self.update_delete_button_state)

        header = self.client_table.horizontalHeader()
        # Estirar todas las columnas excepto la última
        for i in range(self.client_table.columnCount() - 1):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        # La última (columna del botón "Editar") que tenga tamaño fijo o contenido ajustado
        header.setSectionResizeMode(self.client_table.columnCount() - 1, QHeaderView.ResizeToContents)
        self.load_clients()

        self.setLayout(layout)

    def load_clients(self):
        self.all_clients = Client.get_all()
        self.total_label.setText(f"Total de clientes: {len(self.all_clients)}")
        self.apply_filters()

    def apply_filters(self):
        text = self.search_input.text().lower()
        only_with_email = self.email_checkbox.isChecked()
        only_with_phone = self.phone_checkbox.isChecked()

        self.filtered_clients = []

        filtered = []
        for client in self.all_clients:
            full_name = f"{client['name']} {client['surname']}".lower()
            if text and text not in full_name:
                continue
            if only_with_email and not client.get("mail"):
                continue
            if only_with_phone and not client.get("phone"):
                continue
            filtered.append(client)

        self.filtered_clients = filtered

        sort_mode = self.sort_combo.currentText()

        if sort_mode == "Ordenar por nombre (A-Z)":
            filtered.sort(key=lambda c: c['name'].lower())
        elif sort_mode == "Ordenar por nombre (Z-A)":
            filtered.sort(key=lambda c: c['name'].lower(), reverse=True)
        elif sort_mode == "Ordenar por apellido (A-Z)":
            filtered.sort(key=lambda c: c['surname'].lower())
        elif sort_mode == "Ordenar por apellido (Z-A)":
            filtered.sort(key=lambda c: c['surname'].lower(), reverse=True)

        self.client_table.setRowCount(len(filtered))

        for row, client in enumerate(filtered):
            self.client_table.setItem(row, 0, QTableWidgetItem(client['name']))
            self.client_table.setItem(row, 1, QTableWidgetItem(client['surname']))
            self.client_table.setItem(row, 2, QTableWidgetItem(client.get('mail') or ""))
            self.client_table.setItem(row, 3, QTableWidgetItem(client.get('phone') or ""))

            # Botón Editar
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda checked, c=client: self.open_client(c))
            self.client_table.setCellWidget(row, 4, btn_edit)

    def open_client(self, client=None):
        dialog = ClientDialog(self, client)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            # Validar campos obligatorios
            name = data.get("name", "").strip()
            surname = data.get("surname", "").strip()

            if not name or not surname:
                QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios.")
                return

            if client:
                # Editar cliente existente
                Client.update(client['id'], data.get("name"), data.get("surname"), data.get("phone"), data.get("mail"))
            else:
                # Crear nuevo cliente
                Client(data.get("name"), data.get("surname"), data.get("phone"), data.get("mail")).save()
            self.load_clients()

    def delete_selected_clients(self):
        selected_rows = self.client_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "No hay clientes seleccionados para eliminar.")
            return

        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       f"¿Estás seguro de eliminar {len(selected_rows)} cliente(s)?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            for index in sorted(selected_rows, reverse=True):
                client_id = self.filtered_clients[index.row()]['id']
                Client.delete(client_id)
            self.load_clients()

    def update_delete_button_state(self):
        selected_rows = self.client_table.selectionModel().selectedRows()
        self.btn_delete_selected.setEnabled(len(selected_rows) > 0)
