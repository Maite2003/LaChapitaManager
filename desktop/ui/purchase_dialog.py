from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QHeaderView, QDateEdit, QSpinBox
)
from core.product_services import ProductService
from core.agenda_services import AgendaService

class PurchaseDialog(QDialog):
    def __init__(self, parent=None, purchase=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_suppliers()
        self.purchase = purchase
        if purchase:
            self.load_purchase()

    def setup_ui(self):
        self.setWindowTitle("Agregar compra")
        self.setMinimumSize(600, 400)

        self.layout = QVBoxLayout(self)

        # Supplier
        supplier_layout = QHBoxLayout()
        supplier_layout.addWidget(QLabel("Proveedor:"))
        self.supplier_combo = QComboBox()
        supplier_layout.addWidget(self.supplier_combo)
        self.layout.addLayout(supplier_layout)

        # Date
        date_label = QLabel("Fecha de venta:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())  # By default, today
        self.date_edit.setMaximumDate(QDate.currentDate())  # Don't allow future dates

        self.layout.addWidget(date_label)
        self.layout.addWidget(self.date_edit)

        # Products table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Producto", "Variante", "Cantidad", "Unidad", "Precio unitario", "Total", " "])
        self.layout.addWidget(self.table)

        # New row button
        self.add_row_btn = QPushButton("Agregar producto")
        self.add_row_btn.clicked.connect(self.add_product_row)
        self.layout.addWidget(self.add_row_btn)

        # Total
        self.total_label = QLabel("Total: $0")
        self.layout.addWidget(self.total_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(button_layout)

    def load_suppliers(self):
        self.supplier_combo.addItem("Sin proveedor", None)
        for supplier in AgendaService.get_all_suppliers():
            name = f"{supplier['name']} {supplier['surname']}"
            self.supplier_combo.addItem(name, supplier['id'])

    def add_product_row(self, product_id=None, variant_id=None, quantity=1, unit_price=0.0, active=True):
        def load_variants(product=None, variant_id=None):
            variant_combo.setEnabled(True)
            variant_combo.clear()
            for v in product['variants']:
                variant_combo.addItem(v['variant_name'], v['id'])
            if variant_id:
                item = variant_combo.findData(variant_id)
                variant_combo.setCurrentIndex(item)
            else:
                variant_combo.setCurrentIndex(0)

        def on_product_selected(variant_id=None, product_id=None):
            product = ProductService.get_product_by_id(product_id)
            unit_label.setText(product['unit'])

            if not variant_id and product['variants'] != []:
                load_variants(product=product)
            elif variant_id:
                load_variants(product=product ,variant_id=variant_id)
            else:
                variant_combo.setEnabled(False)
                variant_combo.clear()
                variant_combo.addItem("Sin variantes", None)

            self.update_row_total(row=row)

        posibilities = ProductService.get_all_products(active=1)

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Product
        product_combo = QComboBox()
        for item in posibilities:
            product_combo.addItem(item["name"], item["id"])
        self.table.setCellWidget(row, 0, product_combo)
        product_combo.currentIndexChanged.connect(lambda: on_product_selected(product_id=product_combo.currentData()))
        product_combo.setCurrentIndex(0)  # Set the first product as selected

        # Variant
        variant_combo = QComboBox()
        self.table.setCellWidget(row, 1, variant_combo)
        variant_combo.setEnabled(False)  # Initially disabled

        # Quantity
        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setValue(1)
        qty_spin.setMaximum(9999)  # Set a reasonable maximum
        self.table.setCellWidget(row, 2, qty_spin)
        qty_spin.valueChanged.connect(lambda: self.update_row_total(row=row))

        # Unit
        unit_label = QLabel("-")
        self.table.setCellWidget(row, 3, unit_label)

        # Unit price
        price_spin = QDoubleSpinBox()
        price_spin.setMinimum(1)
        price_spin.setMaximum(999999)  # Set a reasonable maximum
        price_spin.setValue(1)
        self.table.setCellWidget(row, 4, price_spin)
        price_spin.setPrefix("$")
        price_spin.valueChanged.connect(lambda: self.update_row_total(row=row))

        # Total per row
        total_label = QLabel("$0.00")
        self.table.setCellWidget(row, 5, total_label)

        # Delete button
        delete_btn = QPushButton("x")
        delete_btn.setToolTip("Eliminar producto")
        delete_btn.clicked.connect(lambda: self.delete_product_row(row))
        self.table.setCellWidget(row, 6, delete_btn)


        if product_id: # Editing
            qty_spin.setValue(quantity)
            price_spin.setValue(unit_price)
            # If a product ID is provided, set it in the combo box
            index = product_combo.findData(product_id)
            if index != -1:
                product_combo.setCurrentIndex(index)

            if not active:
                product_combo.setEnabled(False)
                variant_combo.setEnabled(False)
                price_spin.setEnabled(False)
                qty_spin.setEnabled(False)
                delete_btn.setEnabled(False)

        on_product_selected(product_id=product_combo.currentData(), variant_id=variant_combo.currentData())

    def update_row_total(self, row):
        qty_spin = self.table.cellWidget(row, 2)
        price_spin = self.table.cellWidget(row, 4)
        total_label = self.table.cellWidget(row, 5)

        qty = qty_spin.value()
        price = price_spin.value()
        total = qty * price
        total_label.setText(f"${total:.2f}")
        self.update_total()

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

    def get_data(self):
        supplier_id = self.supplier_combo.currentData()
        date = self.date_edit.date().toString("dd-MM-yyyy")
        details = []

        for row in range(self.table.rowCount()):
            product_combo = self.table.cellWidget(row, 0)
            active = product_combo.isEnabled()
            variant_combo = self.table.cellWidget(row, 1)
            qty_spin = self.table.cellWidget(row, 2)
            price_spin = self.table.cellWidget(row, 4)

            product_id = product_combo.currentData()
            variant_id = variant_combo.currentData() if variant_combo else None
            qty = qty_spin.value()
            price = price_spin.value()
            details.append((product_id, variant_id, qty, price, active))

        purchase_id = None
        if self.purchase:
            purchase_id = self.purchase["id"]
        return {"id": purchase_id, "items": details, "supplier_id": supplier_id, "date": date}

    def delete_product_row(self, row):
        self.table.removeRow(row)
        self.update_total()

    def load_purchase(self):
        self.load_suppliers()
        if self.purchase["supplier_id"]: self.supplier_combo.setCurrentIndex(self.supplier_combo.findData(self.purchase["supplier_id"]))
        date = QDate.fromString(self.purchase["date"], "dd-MM-yyyy")
        self.date_edit.setDate(date)

        self.table.setRowCount(0)  # Clear existing rows
        for key, details in self.purchase["items"].items():
            product_id, variant_id = key
            quantity = details["quantity"]
            unit_price = details["unit_price"]
            active = details["active"]
            self.add_product_row(product_id=product_id, variant_id=variant_id, quantity=quantity, unit_price=unit_price, active=active)

        self.update_total()

