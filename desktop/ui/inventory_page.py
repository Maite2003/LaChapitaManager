from functools import partial

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QToolButton
)
from PySide6.QtCore import Qt, Signal
from services.product_services import ProductService
from .product_dialog import AddProductDialog


class InventoryPage(QWidget):
    product_changed = Signal()
    def __init__(self):
        super().__init__()
        self.setup_iu()

        # Show the total products at the beginning
        self.reset_filters()
        self.load_filtered_products()

    def setup_iu(self):
        main_layout = QVBoxLayout(self)

        # Total product
        self.total_label = QLabel("Total productos: 0")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.total_label)

        # Layout for search and filters
        filters_layout = QHBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar por título...")
        filters_layout.addWidget(self.search_bar, 3)  # peso 3 para que sea más ancho

        # ComboBox for categories
        self.category_filter = QComboBox()
        filters_layout.addWidget(self.category_filter, 2)

        # Checkbox for low_stock
        self.low_stock_cb = QCheckBox("Bajo stock")
        filters_layout.addWidget(self.low_stock_cb)

        # Checkbox for out of stock
        self.no_stock_cb = QCheckBox("Sin stock")
        filters_layout.addWidget(self.no_stock_cb)

        # New product
        self.add_product_btn = QPushButton("Nuevo")
        self.add_product_btn.clicked.connect(self.open_product_dialog)
        filters_layout.addWidget(self.add_product_btn)

        # Delete products
        self.delete_products_btn = QPushButton("Eliminar")
        self.delete_products_btn.setEnabled(False)
        self.delete_products_btn.clicked.connect(self.delete_selected_products)
        filters_layout.addWidget(self.delete_products_btn)

        main_layout.addLayout(filters_layout)

        # Product's table
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Id (hidden), Name, Category, Variants, Stock, Edit button
        self.table.setHorizontalHeaderLabels(["Id", "Nombre", "Categoría", "Variantes", "Stock", "      "])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self.update_delete_button_state)
        main_layout.addWidget(self.table)

        # Reset column
        header = self.table.horizontalHeader()
        # Stretch the columns 1 to 4
        for i in range(1, self.table.columnCount() - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # Make edit col fit the content
        header.setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.ResizeMode.ResizeToContents)

        # Connect filters so the table updates automatically
        self.search_bar.textChanged.connect(self.load_filtered_products)
        self.category_filter.currentIndexChanged.connect(self.load_filtered_products)
        self.low_stock_cb.stateChanged.connect(self.load_filtered_products)
        self.no_stock_cb.stateChanged.connect(self.load_filtered_products)

    def reset_filters(self):
        categories = ProductService.get_all_categories()
        self.category_filter.clear()
        self.category_filter.addItem("Todas las categorías", None)
        for cat in categories:
            self.category_filter.addItem(cat["name"], cat["id"])

        self.low_stock_cb.setChecked(False)
        self.no_stock_cb.setChecked(False)
        self.search_bar.clear()

    def update_delete_button_state(self):
        selected = self.table.selectionModel().selectedRows()
        if len(selected) == 0:
            self.delete_products_btn.setEnabled(False)
        else:
            self.delete_products_btn.setEnabled(True)

    def delete_selected_products(self):
        selected = self.table.selectionModel().selectedRows()

        reply = QMessageBox.question(self, "Confirmar eliminación",
                                     f"¿Estás seguro de que quieres eliminar {len(selected)} producto/s ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for row in selected:
                product_id = self.table.item(row.row(), 0).text()
                ProductService.delete_product(int(product_id))
            self.refresh()

    def load_filtered_products(self):
        def is_variant_low(variants):
            for v in variants:
                if v["stock"] <= v["stock_low"]:
                    return True
            return False

        def is_variant_no_stock(variants):
            for v in variants:
                if v["stock"] == 0:
                    return True
            return False

        def get_filtered_products():
            text = self.search_bar.text().lower()
            category = self.category_filter.currentText()
            low_stock = self.low_stock_cb.isChecked()
            no_stock = self.no_stock_cb.isChecked()

            products = ProductService.get_all_products(active=1)

            filtered = []
            for p in products:
                if text and text not in p["name"].lower():
                    continue
                if category != "Todas las categorías" and p["category"] != category:
                    continue
                if len(p['variants']) == 0:
                    if low_stock and p["stock"] <= p["stock_low"]:
                        pass
                    else:
                        if low_stock and p["stock"] > p["stock_low"]:
                            continue
                        elif no_stock and p["stock"] != 0:
                            continue
                else:
                    if low_stock and is_variant_low(p["variants"]):
                        pass
                    else:
                        if low_stock and not is_variant_low(p["variants"]):
                            continue
                        elif no_stock and not is_variant_no_stock(p["variants"]):
                            continue
                filtered.append(p)
            return sorted(filtered, key=lambda x: x["name"].lower())

        filtered = get_filtered_products()

        # Update total products label
        self.total_label.setText(f"Total productos: {len(filtered)}")

        # Update table
        self.table.setRowCount(len(filtered))
        for row, product in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
            self.table.setColumnHidden(0, True)  # Hide the ID column

            self.table.setItem(row, 1, QTableWidgetItem(product["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(product["category"]))
            # Show amount of variables
            variant_count = len(product.get("variants", []))
            self.table.setItem(row, 3, QTableWidgetItem(str(variant_count)))
            stock_item = QTableWidgetItem(str(product["stock"]))
            if variant_count == 0:
                # Stock in red if 0
                if product["stock"] == 0:
                    stock_item.setForeground(Qt.GlobalColor.red)
                # Stock in yellow if below the low stock threshold
                elif product["stock"] <= product["stock_low"]:
                    stock_item.setForeground(Qt.GlobalColor.darkYellow)
                else:
                    # Else green
                    stock_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 4, stock_item)
            # Edit button
            details_btn = QToolButton()
            details_btn.setText("Detalles")
            details_btn.clicked.connect(partial(self.open_product_dialog, product))
            self.table.setCellWidget(row, 5, details_btn)

    def refresh(self):
        """
        Updates the product list and emits a signal to notify other components.
        """
        self.table.selectionModel().clearSelection()  # Clear selection
        self.product_changed.emit()
        self.reset_filters()
        self.load_filtered_products()

    def open_product_dialog(self, p=None):
        dialog = AddProductDialog(product=p, parent=self)

        if dialog.exec() == AddProductDialog.DialogCode.Accepted:
            data = dialog.get_data()
            variants = data.get('variants', [])

            if variants:
                data['price'] = -1
                data['stock'] = sum(v['stock'] for v in variants)
                data['stock_low'] = -1
            try:
                if p:
                    ProductService.update_product(data)
                else:
                    ProductService.create_product(data)
            except Exception as e:
                return QMessageBox.critical(self, "Error", f"No se pudo guardar el producto:\n{str(e)}")
            self.refresh()

