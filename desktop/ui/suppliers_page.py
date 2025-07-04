from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QCheckBox, QPushButton, QDialog, QHeaderView, QMessageBox, QToolButton
)
from services.agenda_services import AgendaService
from PySide6.QtCore import Qt

from .supplier_dialog import SupplierDialog


class SuppliersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        self.reset_filters()
        self.load_suppliers()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Total Suppliers
        self.total_label = QLabel("Total de proveedores: 0")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.total_label)

        # Search and filters
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o apellido...")
        self.search_input.textChanged.connect(self.load_suppliers)

        self.email_checkbox = QCheckBox("Con email")
        self.email_checkbox.stateChanged.connect(self.load_suppliers)

        self.phone_checkbox = QCheckBox("Con celular")
        self.phone_checkbox.stateChanged.connect(self.load_suppliers)

        # Button for new supplier
        btn_new_supplier = QPushButton("Nuevo")
        btn_new_supplier.clicked.connect(self.open_supplier)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.email_checkbox)
        filter_layout.addWidget(self.phone_checkbox)
        filter_layout.addWidget(btn_new_supplier)

        self.btn_delete_selected = QPushButton("Eliminar")
        self.btn_delete_selected.setEnabled(False)  # Initially disabled
        self.btn_delete_selected.clicked.connect(self.delete_selected_suppliers)
        filter_layout.addWidget(self.btn_delete_selected)

        layout.addLayout(filter_layout)

        # Supplier's table
        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(6)
        self.supplier_table.setHorizontalHeaderLabels(["Id", "Nombre", "Apellido", "Email", "Celular", "       "])
        self.supplier_table.setColumnHidden(0, True)
        self.supplier_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.supplier_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.supplier_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.supplier_table.setSortingEnabled(True)
        self.supplier_table.itemSelectionChanged.connect(self.update_delete_button_state)

        # Resize cols
        header = self.supplier_table.horizontalHeader()
        # Stretch all columns except the last one
        for i in range(self.supplier_table.columnCount() - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # The last column (Edit button) will resize to contents
        header.setSectionResizeMode(self.supplier_table.columnCount() - 1, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.supplier_table)

    def reset_filters(self):
        self.search_input.clear()
        self.email_checkbox.setChecked(False)
        self.phone_checkbox.setChecked(False)

    def update_delete_button_state(self):
        selected_rows = self.supplier_table.selectionModel().selectedRows()
        self.btn_delete_selected.setEnabled(len(selected_rows) > 0)

    def delete_selected_suppliers(self):
        selected_rows = self.supplier_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "No hay proveedores seleccionados para eliminar.")
            return

        confirm = QMessageBox.question(self, "Confirmar eliminación",
                                       f"¿Estás seguro de eliminar {len(selected_rows)} proveedore(s)?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            for supplier in selected_rows:
                supplier_id = self.supplier_table.item(supplier.row(), 0).text()
                AgendaService.delete_supplier(int(supplier_id))
            self.load_suppliers()

    def load_suppliers(self):
        def get_filtered_suppliers():
            text = self.search_input.text().lower()
            only_with_email = self.email_checkbox.isChecked()
            only_with_phone = self.phone_checkbox.isChecked()

            filtered = []
            for supplier in AgendaService.get_all_suppliers():
                full_name = f"{supplier['name']} {supplier['surname']}".lower()
                if text and text not in full_name:
                    continue
                if only_with_email and not supplier.get("mail"):
                    continue
                if only_with_phone and not supplier.get("phone"):
                    continue
                filtered.append(supplier)

            return sorted(filtered, key=lambda c: (c['name'].lower(), c['surname'].lower()))

        filtered = get_filtered_suppliers()

        self.total_label.setText(f"Total de proveedores: {len(filtered)}")

        self.supplier_table.setRowCount(len(filtered))
        for row, client in enumerate(filtered):
            self.supplier_table.setItem(row, 0, QTableWidgetItem(client['id']))
            self.supplier_table.setItem(row, 1, QTableWidgetItem(client['name']))
            self.supplier_table.setItem(row, 2, QTableWidgetItem(client['surname']))
            self.supplier_table.setItem(row, 3, QTableWidgetItem(client.get('mail') or ""))
            self.supplier_table.setItem(row, 4, QTableWidgetItem(client.get('phone') or ""))

            # Button edit
            btn_edit = QToolButton()
            btn_edit.setText("Editar")
            btn_edit.setToolTip("Editar proveedor")
            btn_edit.clicked.connect(lambda checked, c=client: self.open_supplier(c))
            self.supplier_table.setCellWidget(row, 5, btn_edit)

        self.supplier_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)  # Sort by name by default

    def open_supplier(self, supplier=None):
        dialog = SupplierDialog(self, supplier)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            # Validate data
            name = data.get("name", "").strip()
            surname = data.get("surname", "").strip()

            if not name or not surname:
                QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios.")
                return

            if supplier:
                # Edit supplier
                AgendaService.update_supplier(supplier['id'], data.get("name"), data.get("surname"), data.get("phone"), data.get("mail"))
            else:
                # New supplier
                AgendaService.add_supplier(data.get("name"), data.get("surname"), data.get("phone"), data.get("mail"))
            self.load_suppliers()

    def refresh(self):
        self.reset_filters()
        self.load_suppliers()
        self.update_delete_button_state()