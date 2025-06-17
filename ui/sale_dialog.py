from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QHeaderView, QDateEdit
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

        # Fecha
        date_label = QLabel("Fecha de venta:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())  # Por defecto, hoy

        # Insertarlo en el layout del formulario o layout principal
        self.layout.addWidget(date_label)
        self.layout.addWidget(self.date_edit)

        # Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Producto", "Variante", "Cantidad", "Unidad", "Precio unitario", "Total", " "])
        self.layout.addWidget(self.table)

        # Botón para agregar fila
        self.add_row_btn = QPushButton("Agregar producto")
        self.add_row_btn.clicked.connect(self.add_product_row)
        self.layout.addWidget(self.add_row_btn)

        # Total
        self.total_label = QLabel("Total:")
        self.layout.addWidget(self.total_label)

        # Botones
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.accept)
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
            if p['stock'] > 0:  # Solo agregar productos con stock disponible
                product_combo.addItem(p['name'], p['id'])
        self.table.setCellWidget(row, 0, product_combo)

        # Variante
        variant_combo = QComboBox()
        self.table.setCellWidget(row, 1, variant_combo)

        # Cantidad
        qty_spin = QDoubleSpinBox()
        qty_spin.setMinimum(0.01)
        qty_spin.setValue(1.0)
        self.table.setCellWidget(row, 2, qty_spin)

        # Unidad
        unit_label = QLabel("-")
        self.table.setCellWidget(row, 3, unit_label)

        # Precio Unitario
        price_label = QLabel("$0.00")
        self.table.setCellWidget(row, 4, price_label)

        # Total por producto
        total_label = QLabel("$0.00")
        self.table.setCellWidget(row, 5, total_label)

        # Botón eliminar
        delete_btn = QPushButton("x")
        delete_btn.setToolTip("Eliminar producto")
        delete_btn.clicked.connect(lambda: self.delete_product_row(row))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setCellWidget(row, 6, delete_btn)

        header = self.table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        def on_variant_selected(index, row):
            variant_combo = self.table.cellWidget(row, 1)
            product_combo = self.table.cellWidget(row, 0)

            product_id = product_combo.currentData()
            product = next((p for p in self.products if p['id'] == product_id), None)
            if not product or 'variants' not in product or not product['variants']:
                return

            variant_id = variant_combo.itemData(index)
            variant = next((v for v in product['variants'] if v['id'] == variant_id), None)
            if variant:
                price_label = self.table.cellWidget(row, 4)
                price_label.setText(f"${variant['price']:.2f}")
                self.update_row_total(row)


        def on_product_selected(index):
            product_id = product_combo.itemData(index)
            product = next((p for p in self.products if p['id'] == product_id), None)
            if not product:
                return
            unit_label.setText(product['unit'])
            price_label.setText(f"${product['price']:.2f}")
            qty_spin.setMaximum(product['stock'])
            qty_spin.valueChanged.connect(lambda: self.update_row_total(row=row))
            self.update_row_total(row=row)

            if 'variants' in product and product['variants']:
                variant_combo.setEnabled(True)
                variant_combo.clear()
                for v in product['variants']:
                    variant_combo.addItem(v['name'], v['id'])
                variant_combo.setCurrentIndex(0)
                on_variant_selected(0, row)
                variant_combo.currentIndexChanged.connect(lambda idx: on_variant_selected(idx, row))
                on_variant_selected(variant_combo.currentIndex(), row)

            else:
                variant_combo.setEnabled(False)
                variant_combo.clear()
                variant_combo.addItem("Sin variantes", None)
                variant_combo.setCurrentIndex(0)
        product_combo.currentIndexChanged.connect(on_product_selected)
        on_product_selected(product_combo.currentIndex())



    def update_row_total(self, row):
        qty_spin = self.table.cellWidget(row, 2)
        price_label = self.table.cellWidget(row, 4)
        total_label = self.table.cellWidget(row, 5)

        if not (isinstance(qty_spin, QDoubleSpinBox) and
                isinstance(price_label, QLabel) and
                isinstance(total_label, QLabel)):
            return

        qty = qty_spin.value()
        price_text = price_label.text().replace("$", "").strip()
        try:
            price = float(price_text)
        except ValueError:
            price = 0.0
        total = qty * price
        total_label.setText(f"${total:.2f}")
        print(f"Row {row} total updated to ${total:.2f}")
        self.update_total()

    def update_total(self):
        total = 0.0
        print("Calculating total")
        for row in range(self.table.rowCount()):
            total_label = self.table.cellWidget(row, 5)
            if isinstance(total_label, QLabel):
                total_text = total_label.text().replace("$", "").strip()
                try:
                    total += float(total_text)
                except ValueError:
                    continue
        self.total_label.setText(f"Total: ${total:.2f}")

    def get_data(self):
        client_id = self.client_combo.currentData()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        details = []

        for row in range(self.table.rowCount()):
            product_combo = self.table.cellWidget(row, 0)
            variant_combo = self.table.cellWidget(row, 1)
            qty_spin = self.table.cellWidget(row, 2)
            price_spin = self.table.cellWidget(row, 4)

            if not (isinstance(product_combo, QComboBox) and isinstance(variant_combo, QComboBox) and
                    isinstance(qty_spin, QDoubleSpinBox) and
                    isinstance(price_spin, QLabel)):
                continue

            product_id = product_combo.currentData()
            variant_id = variant_combo.currentData() if variant_combo else None
            qty = qty_spin.value()
            price = price_spin.text().replace("$", "").strip()

            try:
                qty = float(qty)
                price = float(price)
            except ValueError:
                pass

            details.append((product_id, variant_id, qty, price))

        return {"details": details, "client_id": client_id, "date": date}

    def delete_product_row(self, row):
        self.table.removeRow(row)
        self.update_total()
