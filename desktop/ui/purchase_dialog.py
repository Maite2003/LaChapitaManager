from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QLabel, QDoubleSpinBox, QComboBox, QPushButton, QSpinBox
)
from core.product_services import ProductService
from core.agenda_services import AgendaService
from desktop.ui.transaction_dialog_layout import TransactionDialogLayout


class PurchaseDialog(QDialog):
    def __init__(self, parent=None, purchase=None):
        super().__init__(parent)

        self.setWindowTitle("Agregar venta")
        self.setMinimumSize(700, 400)

        self.layout = TransactionDialogLayout(self)
        self.setLayout(self.layout)
        self.layout.person_label.setText("Proveedor")

        self.table = self.layout.get_table()

        self.load_suppliers()
        self.purchase = purchase
        if purchase:
            self.load_purchase()


    def load_suppliers(self):
        self.layout.person_combo.clear()
        self.layout.add_person_combo("Sin proveedor", None)
        for supplier in AgendaService.get_all_suppliers():
            name = f"{supplier['name']} {supplier['surname']}"
            self.layout.add_person_combo(name, supplier['id'])

    def add_product_row(self, product_id=None, variant_id=None, quantity=1, unit_price=0.0, active=True):
        def on_product_selected():
            def load_variants(p=None):
                variant_combo.setEnabled(True)
                variant_combo.clear()
                for v in p['variants']:
                    variant_combo.addItem(v['variant_name'], v['id'])
                if variant_id:
                    variant_combo.setCurrentIndex(variant_combo.findData(variant_id))
                else:
                    variant_combo.setCurrentIndex(0)

            product = ProductService.get_product_by_id(int(self.table.cellWidget(row, 0).currentData()))
            unit_label.setText(product['unit'])

            if not variant_id and product['variants'] != []:
                load_variants(p=product)
            elif variant_id:
                load_variants(p=product)
            else:
                variant_combo.setEnabled(False)
                variant_combo.clear()
                variant_combo.addItem("Sin variantes", None)

            self.update_row_total(row=row)

        possibilities = ProductService.get_all_products(active=1)

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Product
        product_combo = QComboBox()
        for item in possibilities:
            product_combo.addItem(item["name"], item["id"])
        self.table.setCellWidget(row, 0, product_combo)
        product_combo.currentIndexChanged.connect(on_product_selected)
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
        price_spin.setMinimum(0)
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

        on_product_selected()

    def update_row_total(self, row):
        qty_spin = self.table.cellWidget(row, 2)
        price_spin = self.table.cellWidget(row, 4)
        total_label = self.table.cellWidget(row, 5)

        qty = qty_spin.value()
        price = price_spin.value()
        total = qty * price
        total_label.setText(f"${total:.2f}")
        self.layout.update_total()

    def get_data(self):
        supplier_id = self.layout.get_person_combo()
        date = self.layout.get_date_edit().toString("dd-MM-yyyy")
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
        self.layout.update_total()

    def load_purchase(self):
        self.load_suppliers()
        if self.purchase["supplier_id"]: self.layout.set_person_index(self.layout.find_person_index(self.purchase["supplier_id"]))
        date = QDate.fromString(self.purchase["date"], "dd-MM-yyyy")
        self.layout.set_date_edit(date)

        self.table.setRowCount(0)  # Clear existing rows
        for key, details in self.purchase["items"].items():
            product_id, variant_id = key
            quantity = details["quantity"]
            unit_price = details["unit_price"]
            active = details["active"]
            self.add_product_row(product_id=product_id, variant_id=variant_id, quantity=quantity, unit_price=unit_price, active=active)

        self.layout.update_total()

