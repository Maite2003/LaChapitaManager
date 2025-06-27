from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QHeaderView, QDateEdit, QSpinBox
)
from core.product_services import ProductService
from core.agenda_services import AgendaService

class AddSaleDialog(QDialog):
    def __init__(self, parent=None, sale=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_clients()
        self.sale = sale
        self.details = {}

        if sale:
            self.details = sale.get("items", {})
            self.load_sale()

    def setup_ui(self):
        self.setWindowTitle("Agregar venta")
        self.setMinimumSize(600, 400)

        self.layout = QVBoxLayout(self)

        # Cliente
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Cliente:"))
        self.client_combo = QComboBox()
        client_layout.addWidget(self.client_combo)
        self.layout.addLayout(client_layout)

        # Fecha
        date_label = QLabel("Fecha de venta:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())  # By default, today
        self.date_edit.setMaximumDate(QDate.currentDate())  # Don't allow future dates

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
        self.total_label = QLabel("Total: $0")
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

    def load_clients(self):
        self.client_combo.addItem("Sin cliente", None)
        for client in AgendaService.get_all_clients():
            name = f"{client['name']} {client['surname']}"
            self.client_combo.addItem(name, client['id'])

    def get_data(self):
        client_id = self.client_combo.currentData()
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
            price = price_spin.text().replace("$", "").strip()

            try:
                qty = float(qty)
                price = float(price)
            except ValueError:
                pass
            details.append((product_id, variant_id, qty, price, active))

        sale_id = None
        if self.sale:
            sale_id = self.sale["id"]
        return {"id": sale_id, "items": details, "client_id": client_id, "date": date}

    def load_sale(self):
        self.load_clients()
        if self.sale["client_id"]: self.client_combo.setCurrentIndex(self.client_combo.findData(self.sale["client_id"]))
        date = QDate.fromString(self.sale["date"], "dd-MM-yyyy")
        self.date_edit.setDate(date)

        self.table.setRowCount(0)  # Clear existing rows
        for key, details in self.sale["items"].items():
            product_id, variant_id = key
            quantity = details["quantity"]
            unit_price = details["unit_price"]
            active = details["active"]
            self.add_product_row(product_id=product_id, variant_id=variant_id, quantity=quantity, unit_price=unit_price, active=active)

        self.update_total()

    # Details section
    def add_product_row(self, product_id=None, variant_id=None, quantity=0, unit_price=0.0, active=True):
        def getPosibilities():
            posibilities = {}
            for product in ProductService.get_all_products(active=1):
                if len(product["variants"]) > 0:
                    variants = []
                    for variant in product["variants"]:
                        if variant["stock"] > 0:
                            # Add variant only if it has stock
                            variants.append(variant)
                    if len(variants) > 0:
                        posibilities[product["id"]] = product["name"]
                elif product["stock"] > 0: # If the product doesn't have variants, check if it has stock
                    posibilities[product["id"]] = product["name"]

            # Add the products of the sale so they can be on the combo box
            if self.sale['items']:
                for key, value in self.sale['items'].items():
                    if key[0] not in posibilities:
                        posibilities[key[0]] = ProductService.get_product_by_id(key[0])["name"]


            return posibilities

        def on_variant_selected():
            variant_combo = self.table.cellWidget(row, 1)
            product_combo = self.table.cellWidget(row, 0)

            product_id = product_combo.currentData()
            variant_id = variant_combo.currentData()

            product = ProductService.get_product_by_id(product_id)

            variant = None
            for v in product['variants']:
                if v["id"] == variant_id:
                    variant = v
                    break

            if variant:
                qty_spin.setMaximum(variant['stock'] + quantity)
                price_label = self.table.cellWidget(row, 4)
                price_label.setText(f"${variant['price']:.2f}")
                self.update_row_total(row)

        def load_variants(price=None, product=None):
            variant_combo.setEnabled(True)
            variant_combo.clear()
            variant = None
            for v in product['variants']:
                if not variant: # Save the first one
                    variant = v
                variant_combo.addItem(v['variant_name'], v['id'])
            if variant_id:
                item = variant_combo.findData(variant_id)
                variant_combo.setCurrentIndex(item)
            else:
                variant_combo.setCurrentIndex(0)

            if price:
                price_label.setText(f"${price:.2f}")
            else:
                price_label.setText(f"${variant['price']:.2f}")

            on_variant_selected()

        def on_product_selected(price=None, product_id=None):
            product = ProductService.get_product_by_id(product_id)
            unit_label.setText(product['unit'])

            if product['variants'] == []: # The product has no variants
                qty_spin.setMaximum(product['stock'] + quantity)
                price_label.setText(f"${product['price']:.2f}")
                variant_combo.setEnabled(False)
                variant_combo.clear()
                variant_combo.addItem("Sin variantes", None)
                variant_combo.setCurrentIndex(0)
            elif not variant_id: # The product has variants but no variant_id is provided
                load_variants(product=product)
            elif variant_id: # The product has variants and a variant_id is provided
                load_variants(price=price, product=product)


            self.update_row_total(row=row)

        posibilities = getPosibilities()
        if len(posibilities) == 0:
            QMessageBox.warning(self, "Advertencia", "Todos los productos ya han sido agregados.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Product
        product_combo = QComboBox()
        for key, name in posibilities.items():
            product_combo.addItem(name, key)
        self.table.setCellWidget(row, 0, product_combo)
        product_combo.currentIndexChanged.connect(lambda: on_product_selected(product_id=product_combo.currentData()))
        product_combo.setCurrentIndex(0)  # Set the first product as selected

        # Variant
        variant_combo = QComboBox()
        self.table.setCellWidget(row, 1, variant_combo)
        variant_combo.currentIndexChanged.connect(lambda: on_variant_selected())

        # Quantity
        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setValue(1)
        self.table.setCellWidget(row, 2, qty_spin)
        qty_spin.valueChanged.connect(lambda: self.update_row_total(row=row))

        # Amount
        unit_label = QLabel("-")
        self.table.setCellWidget(row, 3, unit_label)

        # Unit price
        price_label = QLabel("$0.00")
        self.table.setCellWidget(row, 4, price_label)

        # Total per row
        total_label = QLabel("$0.00")
        self.table.setCellWidget(row, 5, total_label)

        # Delete button
        delete_btn = QPushButton("x")
        delete_btn.setToolTip("Eliminar producto")
        delete_btn.clicked.connect(lambda: self.delete_product_row(row))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setCellWidget(row, 6, delete_btn)

        header = self.table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)


        if product_id:
            qty_spin.setValue(quantity)
            # If a product ID is provided, set it in the combo box
            index = product_combo.findData(product_id)
            if index != -1:
                product_combo.setCurrentIndex(index)

            if not active:
                product_combo.setEnabled(False)
                variant_combo.setEnabled(False)
                qty_spin.setEnabled(False)
                delete_btn.setEnabled(False)

        on_product_selected(price=unit_price, product_id=product_id)

    def delete_product_row(self, row):
        self.table.removeRow(row)
        self.update_total()

    # Totals
    def update_row_total(self, row):
        qty_spin = self.table.cellWidget(row, 2)
        price_label = self.table.cellWidget(row, 4)
        total_label = self.table.cellWidget(row, 5)

        if not (isinstance(qty_spin, QSpinBox) and
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
