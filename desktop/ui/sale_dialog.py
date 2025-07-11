
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDialog, QLabel, QMessageBox,
    QComboBox, QHeaderView, QSpinBox, QToolButton
)
from services.product_services import ProductService
from services.agenda_services import AgendaService
from .transaction_dialog_layout import TransactionDialogLayout


class AddSaleDialog(QDialog):
    def __init__(self, parent=None, sale=None):
        super().__init__(parent)

        self.setWindowTitle("Agregar compra")
        self.setMinimumSize(700, 400)

        self.layout = TransactionDialogLayout(self)
        self.setLayout(self.layout)
        self.layout.person_label.setText("Cliente")
        self.table = self.layout.get_table()

        self.load_clients()
        self.sale = sale
        self.details = {}

        if sale:
            self.details = sale.get("items", {})
            self.load_sale()

    def load_clients(self):
        self.layout.person_combo.clear()
        self.layout.add_person_combo("Sin cliente", None)
        for client in AgendaService.get_all_clients():
            name = f"{client['name']} {client['surname']}"
            self.layout.add_person_combo(name, client['id'])

    def get_data(self):
        client_id = self.layout.get_person_combo()
        date = self.layout.get_date_edit().toString("dd-MM-yyyy")
        details = []

        for row in range(self.table.rowCount()):
            product_combo = self.table.cellWidget(row, 0)
            active = product_combo.isEnabled()
            variant_combo = self.table.cellWidget(row, 1)
            qty_spin = self.table.cellWidget(row, 2)
            price_spin = self.table.cellWidget(row, 4)

            if not (isinstance(product_combo, QComboBox) and
                    isinstance(qty_spin, QSpinBox) and
                    isinstance(variant_combo, QComboBox) and
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
            details.append((product_id, variant_id, qty, price, active))

        sale_id = None
        if self.sale:
            sale_id = self.sale["id"]
        return {"id": sale_id, "items": details, "client_id": client_id, "date": date}

    def load_sale(self):
        self.load_clients()
        if self.sale["client_id"]: self.layout.set_person_index(self.layout.find_person_index(self.sale["client_id"]))

        date = QDate.fromString(self.sale["date"], "dd-MM-yyyy")
        self.layout.set_date_edit(date)

        self.table.setRowCount(0)  # Clear existing rows
        for key, details in self.sale["items"].items():
            product_id, variant_id = key
            quantity = details["quantity"]
            unit_price = details["unit_price"]
            active = details["active"]
            self.add_product_row(product_id=product_id, variant_id=variant_id, quantity=quantity, unit_price=unit_price, active=active)

        self.layout.update_total()

    # Details section
    def add_product_row(self, product_id=None, variant_id=None, quantity=0, unit_price=0.0, active=True):

        def get_possibilities():
            options = {}
            for product in ProductService.get_all_products(active=1):
                if len(product["variants"]) > 0: # Has variants
                    variants = []
                    for variant in product["variants"]:
                        if variant["stock"] > 0: # If it has stock
                            variants.append(variant)
                    if len(variants) > 0: # If there are variants with stock
                        product["variants"] = variants
                        options[product["id"]] = product
                elif product["stock"] > 0: # If the product doesn't have variants, check if it has stock
                    options[product["id"]] = product

            # Add the products of the sale so they can be on the combo box
            if self.sale:
                for k, value in self.sale['items'].items():
                    if k[0] not in options: # If the product is not already in the options
                        product = ProductService.get_product_by_id(k[0])

                        variants = []
                        if k[1] is not None: # It is a variant
                            variant = ProductService.get_variant_by_id(k[0], k[1])
                            variant['stock'] = value['quantity'] # Set the stock to the quantity of the sale
                            variants.append(variant)

                        product['variants'] = variants
                    else: # Product is already in the options
                        if k[1] is None: # No variants
                            options[k[0]]['stock'] += value['quantity']
                        else: # It is a variant
                            variants = options[k[0]]['variants']
                            variant = None
                            for v in variants:
                                if v['id'] == k[1]:
                                    variant = v
                                    break

                            # Check if variant was there
                            if variant is not None:
                                variant['stock'] += value['quantity']
                            else: # Variant has no stock
                                variant = ProductService.get_variant_by_id(k[0], k[1])
                                variant['stock'] = value['quantity']
                                variants.append(variant)


            return options

        def on_variant_selected():
            variant_c = self.table.cellWidget(row, 1)
            product_c = self.table.cellWidget(row, 0)

            if not isinstance(variant_c, QComboBox) or not isinstance(product_c, QComboBox):
                return

            p_id = product_c.currentData()
            v_id = variant_c.currentData()

            product = ProductService.get_product_by_id(p_id)

            variant = None
            for v in product['variants']:
                if v["id"] == v_id:
                    variant = v
                    break

            if variant:
                qty_spin.setMaximum(variant['stock'] + quantity)
                price = self.table.cellWidget(row, 4)
                if not isinstance(price, QLabel):
                    return
                price.setText(f"${variant['price']:.2f}")
                self.update_row_total(row)

        def load_variants(price=None, product=None):
            variant_combo.setEnabled(True)
            variant_combo.clear()
            variant = None
            for v in possibilities[product['id']]['variants']:
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

        def on_product_selected(price=None):
            product = ProductService.get_product_by_id(int(self.table.cellWidget(row, 0).currentData()))
            unit_label.setText(product['unit'])
            if not product['variants']: # The product has no variants
                if product_id: qty_spin.setMaximum(product['stock'] + quantity)
                else: qty_spin.setMaximum(product['stock'])
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

        possibilities = get_possibilities()
        if len(possibilities) == 0:
            QMessageBox.warning(self, "Advertencia", "Todos los productos ya han sido agregados.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Product
        product_combo = QComboBox()
        print("Productos es ")
        for key, dict in possibilities.items():
            print(f"{dict['name']}")
            for v in dict['variants']:
                print(f"         {v['variant_name']} ")
            product_combo.addItem(dict['name'], key)
        self.table.setCellWidget(row, 0, product_combo)
        product_combo.currentIndexChanged.connect(lambda: on_product_selected())
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
        delete_btn = QToolButton()
        delete_btn.setText("X")
        delete_btn.setToolTip("Eliminar producto")
        delete_btn.clicked.connect(lambda: self.layout.delete_product_row(row))
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

        on_product_selected(price=unit_price)

    # Totals
    def update_row_total(self, row):
        print("Llamando a update_row_total para la fila:", row)
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
        self.layout.update_total()
