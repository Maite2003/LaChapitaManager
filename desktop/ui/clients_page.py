from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QCheckBox, QPushButton, QDialog, QHeaderView, QMessageBox, QComboBox
)
from services.agenda_services import AgendaService
from desktop.ui.client_dialog import ClientDialog
from PySide6.QtCore import Qt


class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        self.reset_filters()
        self.load_clients()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Total Clients
        self.total_label = QLabel("Total de clientes: 0")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.total_label)

        # Search and filters
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o apellido...")
        self.search_input.textChanged.connect(self.load_clients)

        self.email_checkbox = QCheckBox("Con email")
        self.email_checkbox.stateChanged.connect(self.load_clients)

        self.phone_checkbox = QCheckBox("Con celular")
        self.phone_checkbox.stateChanged.connect(self.load_clients)

        # Button for new client
        btn_new_client = QPushButton("Nuevo")
        btn_new_client.clicked.connect(self.open_client)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.email_checkbox)
        filter_layout.addWidget(self.phone_checkbox)
        filter_layout.addWidget(btn_new_client)

        self.btn_delete_selected = QPushButton("Eliminar")
        self.btn_delete_selected.setEnabled(False)  # Initially disabled
        self.btn_delete_selected.clicked.connect(self.delete_selected_clients)
        filter_layout.addWidget(self.btn_delete_selected)

        layout.addLayout(filter_layout)

        # Client's table
        self.client_table = QTableWidget()
        self.client_table.setColumnCount(6)
        self.client_table.setHorizontalHeaderLabels(["Id", "Nombre", "Apellido", "Email", "Celular", "       "])
        self.client_table.setColumnHidden(0, True)
        self.client_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.client_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.client_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.client_table.setSortingEnabled(True)
        self.client_table.itemSelectionChanged.connect(self.update_delete_button_state)

        # Resize cols
        header = self.client_table.horizontalHeader()
        # Stretch all columns except the last one
        for i in range(self.client_table.columnCount() - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # The last column (Edit button) will resize to contents
        header.setSectionResizeMode(self.client_table.columnCount() - 1, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.client_table)

    def reset_filters(self):
        self.search_input.clear()
        self.email_checkbox.setChecked(False)
        self.phone_checkbox.setChecked(False)

    def update_delete_button_state(self):
        selected_rows = self.client_table.selectionModel().selectedRows()
        self.btn_delete_selected.setEnabled(len(selected_rows) > 0)

    def delete_selected_clients(self):
        selected_rows = self.client_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "No hay clientes seleccionados para eliminar.")
            return

        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       f"¿Estás seguro de eliminar {len(selected_rows)} cliente(s)?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            for client in selected_rows:
                client_id = self.client_table.item(client.row(), 0).text()
                AgendaService.delete_client(int(client_id))
            self.load_clients()

    def load_clients(self):
        def get_filtered_clients():
            text = self.search_input.text().lower()
            only_with_email = self.email_checkbox.isChecked()
            only_with_phone = self.phone_checkbox.isChecked()

            filtered = []
            for client in AgendaService.get_all_clients():
                full_name = f"{client['name']} {client['surname']}".lower()
                if text and text not in full_name:
                    continue
                if only_with_email and not client.get("mail"):
                    continue
                if only_with_phone and not client.get("phone"):
                    continue
                filtered.append(client)

            return sorted(filtered, key=lambda c: (c['name'].lower(), c['surname'].lower()))


        filtered = get_filtered_clients()

        self.total_label.setText(f"Total de clientes: {len(filtered)}")

        self.client_table.setRowCount(len(filtered))
        for row, client in enumerate(filtered):
            self.client_table.setItem(row, 0, QTableWidgetItem(client['id']))
            self.client_table.setItem(row, 1, QTableWidgetItem(client['name']))
            self.client_table.setItem(row, 2, QTableWidgetItem(client['surname']))
            self.client_table.setItem(row, 3, QTableWidgetItem(client.get('mail') or ""))
            self.client_table.setItem(row, 4, QTableWidgetItem(client.get('phone') or ""))

            # Button edit
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda checked, c=client: self.open_client(c))
            self.client_table.setCellWidget(row, 5, btn_edit)

        self.client_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)  # Sort by name by default

    def open_client(self, client=None):
        dialog = ClientDialog(self, client)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            # Validate data
            name = data.get("name", "").strip()
            surname = data.get("surname", "").strip()

            if not name or not surname:
                QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios.")
                return

            if client:
                # Edit existing client
                AgendaService.update_client(client['id'], data.get("name"), data.get("surname"), data.get("phone"), data.get("mail"))
            else:
                # New client
                AgendaService.add_client(data.get("name"), data.get("surname"), data.get("phone"), data.get("mail"))
            self.load_clients()

    def refresh(self):
        """Refresh the clients page."""
        self.reset_filters()
        self.load_clients()
        self.update_delete_button_state()