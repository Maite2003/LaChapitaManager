from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget
)
import models.sale as Sale
from models.client import Client
from models.product import Product
from datetime import datetime

class AddSaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar venta")
        self.setMinimumSize(600, 400)

        self.layout = QVBoxLayout(self)

        # Cliente
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Cliente:"))
        self.client_combo = QComboBox()
        self.load_clients()
        client_layout.addWidget(self.client_combo)
        self.layout.addLayout(client_layout)

        # Tabla de productos
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio unitario"])
        self.layout.addWidget(self.table)

        # Botón para agregar fila
        self.add_row_btn = QPushButton("Agregar producto")
        self.add_row_btn.clicked.connect(self.add_product_row)
        self.layout.addWidget(self.add_row_btn)

        # Total
        self.total_label = QLabel("Total: $0.00")
        self.layout.addWidget(self.total_label)

        # Botones
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.save_sale)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(button_layout)

        self.products = Product.get_all()
        self.update_total()

    def load_clients(self):
        self.client_combo.addItem("Sin cliente", None)
        for client in Client.get_all():
            name = f"{client['name']} {client['surname']}"
            self.client_combo.addItem(name, client['id'])

    def add_product_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Producto
        product_combo = QComboBox()
        for p in self.products:
            product_combo.addItem(p['title'], p['id'])
        product_combo.currentIndexChanged.connect(self.update_total)
        self.table.setCellWidget(row, 0, product_combo)

        # Cantidad
        qty_spin = QDoubleSpinBox()
        qty_spin.setMinimum(0.01)
        qty_spin.setValue(1.0)
        qty_spin.valueChanged.connect(self.update_total)
        self.table.setCellWidget(row, 1, qty_spin)

        # Precio unitario
        price_spin = QDoubleSpinBox()
        price_spin.setMinimum(0.01)
        price_spin.setValue(1.0)
        price_spin.valueChanged.connect(self.update_total)
        self.table.setCellWidget(row, 2, price_spin)

        self.update_total()

    def update_total(self):
        total = 0
        for row in range(self.table.rowCount()):
            qty = self.table.cellWidget(row, 1).value()
            price = self.table.cellWidget(row, 2).value()
            total += qty * price
        self.total_label.setText(f"Total: ${total:.2f}")

    def save_sale(self):
        client_id = self.client_combo.currentData()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = 0
        details = []

        for row in range(self.table.rowCount()):
            product_id = self.table.cellWidget(row, 0).currentData()
            qty = self.table.cellWidget(row, 1).value()
            price = self.table.cellWidget(row, 2).value()
            total += qty * price
            details.append((product_id, qty, price))

        if not details:
            return QMessageBox.warning(self, "Error", "Agrega al menos un producto.")

        try:
            Sale.save_sale(date=date, client=client_id, items=details)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la venta:\n{str(e)}")
