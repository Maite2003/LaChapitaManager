from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QTableWidget, QPushButton


class TransactionDialogLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()


    def setup_ui(self):
        # Cliente
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Cliente:"))
        self.person_combo = QComboBox()
        client_layout.addWidget(self.person_combo)
        self.addLayout(client_layout)

        # Fecha
        date_label = QLabel("Fecha de venta:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())  # By default, today
        self.date_edit.setMaximumDate(QDate.currentDate())  # Don't allow future dates

        # Insertarlo en el layout del formulario o layout principal
        self.addWidget(date_label)
        self.addWidget(self.date_edit)

        # Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Producto", "Variante", "Cantidad", "Unidad", "Precio unitario", "Total", " "])
        self.addWidget(self.table)

        # Botón para agregar fila
        self.add_row_btn = QPushButton("Agregar producto")
        self.addWidget(self.add_row_btn)

        # Total
        self.total_label = QLabel("Total: $0")
        self.addWidget(self.total_label)

        # Botones
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.cancel_btn = QPushButton("Cancelar")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        self.addLayout(button_layout)


    def get_person_combo(self):
        return self.person_combo.currentData()

    def set_person_index(self, index):
        self.person_combo.setCurrentIndex(index)

    def find_person_index(self, id):
        return self.person_combo.findData(id)

    def get_date_edit(self):
        return self.date_edit.date()

    def set_date_edit(self, date):
        self.date_edit.setDate(date)

    def get_table(self):
        return self.table

    def add_person_combo(self, name, id):
        self.person_combo.addItem(name, id)


    def update_total(self):
        total = 0.0
        for row in range(self.table.rowCount()):
            total_label = self.table.cellWidget(row, 5)
            if isinstance(total_label, QLabel):
                total_text = total_label.text().replace("$", "").strip()
                try:
                    total += float(total_text)
                except ValueError:
                    continue
        self.total_label.setText(f"Total: ${total:.2f}")


    def delete_product_row(self, row):
        self.table.removeRow(row)
        self.update_total()