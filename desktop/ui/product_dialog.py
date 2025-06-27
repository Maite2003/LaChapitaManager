from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QDialog, QDoubleSpinBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QSpinBox
)

from core.product_services import ProductService
import models.units as Units
from desktop.ui.variant_dialog import VariantDialog


class AddProductDialog(QDialog):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.variants = []

        self.setup_ui()
        if self.product:
            self.variants = self.product.get("variants", [])
            self.load_product()

    def setup_ui(self):
        self.setWindowTitle("Agregar producto")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Nombre
        layout.addWidget(QLabel("Nombre:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Unidad
        layout.addWidget(QLabel("Unidad de medida"))
        self.unit_input = QComboBox()
        self.unit_input.addItems(Units.get_all())
        layout.addWidget(self.unit_input)

        # Categoría
        layout.addWidget(QLabel("Categoría:"))
        self.category_combo = QComboBox()
        categories = sorted(c['name'] for c in ProductService.get_all_categories())
        self.category_combo.addItems(categories)
        layout.addWidget(self.category_combo)

        # Precio de venta
        layout.addWidget(QLabel("Precio de venta:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.00)
        self.price_input.setMaximum(999999)
        self.price_input.setValue(1.0)
        layout.addWidget(self.price_input)

        # Initial stock
        layout.addWidget(QLabel("Stock inicial (opcional):"))
        self.stock = QSpinBox()
        self.stock.setMinimum(0)  # Permite 0
        self.stock.setMaximum(999999)
        self.stock.setValue(0)  # Por defecto 0 = sin límite
        layout.addWidget(self.stock)

        # Minimum stock
        layout.addWidget(QLabel("Stock mínimo (opcional):"))
        self.stock_low_input = QSpinBox()
        self.stock_low_input.setMinimum(0)  # Permite 0
        self.stock_low_input.setMaximum(999999)
        self.stock_low_input.setValue(0)  # Por defecto 0 = sin límite
        layout.addWidget(self.stock_low_input)

        ## --- TABLA VARIANTES ---
        layout.addWidget(QLabel("Variantes del producto:"))
        self.variant_table = QTableWidget(0, 4)
        self.variant_table.setHorizontalHeaderLabels(["Variante", "Stock", "Stock minimo", "Precio"])
        self.variant_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.variant_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.variant_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.variant_table.itemSelectionChanged.connect(lambda: self.update_buttons())
        layout.addWidget(self.variant_table)

        variant_btn_layout = QHBoxLayout()
        add_variant_btn = QPushButton("Agregar variante")
        add_variant_btn.clicked.connect(self.add_variant)
        self.edit_variant_btn = QPushButton("Editar variante")
        self.edit_variant_btn.setEnabled(False)
        self.edit_variant_btn.clicked.connect(self.edit_variant)
        self.delete_variant_btn = QPushButton("Eliminar variante")
        self.delete_variant_btn.clicked.connect(self.delete_variant)
        self.delete_variant_btn.setEnabled(False)

        variant_btn_layout.addWidget(add_variant_btn)
        variant_btn_layout.addWidget(self.edit_variant_btn)
        variant_btn_layout.addWidget(self.delete_variant_btn)
        layout.addLayout(variant_btn_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def update_buttons(self):
        selected = self.variant_table.selectionModel().selectedRows()
        if len(selected) == 0:
            self.edit_variant_btn.setEnabled(False)
            self.delete_variant_btn.setEnabled(False)
        elif len(selected) == 1:
            self.edit_variant_btn.setEnabled(True)
            self.delete_variant_btn.setEnabled(True)
        else:
            self.edit_variant_btn.setEnabled(False)
            self.delete_variant_btn.setEnabled(True)

    def load_product(self):
        index = self.unit_input.findText(self.product["unit"])
        if index != -1:
            self.unit_input.setCurrentIndex(index)

        category = self.category_combo.findText(self.product["category"])
        if category != -1:
            self.category_combo.setCurrentIndex(category)

        self.name_input.setText(self.product["name"])
        self.price_input.setValue(self.product["price"])
        self.stock.setValue(self.product["stock"])
        self.stock_low_input.setValue(self.product["stock_low"])

        self.refresh_variant_table()

    def get_data(self):
        name = self.name_input.text().strip()
        unit = self.unit_input.currentText().strip()
        category = self.category_combo.currentText()
        stock_low = self.stock_low_input.value()
        stock = self.stock.value()

        """Devuelve los datos del producto como un diccionario."""
        return {
            "id": self.product["id"] if self.product else None,
            "name": name,
            "unit": unit,
            "category": ProductService.get_category_id_by_name(category),
            "price": self.price_input.value(),
            "stock": stock,
            "stock_low": stock_low,
            "variants": self.variants
        }

    # Variants seccion

    def add_variant(self):
        dialog = VariantDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['variant_name']:
                QMessageBox.warning(self, "Error", "La variante debe tener nombre.")
                return
            self.variants.append(data)
            self.refresh_variant_table()

    def edit_variant(self):
        selected = self.variant_table.currentRow()
        if selected < 0 or selected >= len(self.variants):
            QMessageBox.warning(self, "Error", "Seleccione una variante para editar.")
            return
        dialog = VariantDialog(self, self.variants[selected])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['variant_name']:
                QMessageBox.warning(self, "Error", "La variante debe tener nombre.")
                return
            self.variants[selected] = data
            self.refresh_variant_table()

    def delete_variant(self):
        selected = self.variant_table.currentRow()
        if selected < 0 or selected >= len(self.variants):
            QMessageBox.warning(self, "Error", "Seleccione una variante para eliminar.")
            return
        self.variants.pop(selected)
        self.refresh_variant_table()

    def refresh_variant_table(self):
        self.variant_table.setRowCount(len(self.variants))
        for i, v in enumerate(self.variants):
            self.variant_table.setItem(i, 0, QTableWidgetItem(v['variant_name']))
            self.variant_table.setItem(i, 1, QTableWidgetItem(str(v['stock'])))
            self.variant_table.setItem(i, 2, QTableWidgetItem(str(v['stock_low'])))
            self.variant_table.setItem(i, 3, QTableWidgetItem(f"{v['price']:.2f}"))

            self.variant_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Si hay variantes, actualizar stock y precio y deshabilitar inputs
        if self.variants:
            total_stock = sum(v['stock'] for v in self.variants)
            prices = [v['price'] for v in self.variants]
            min_price = min(prices)
            max_price = max(prices)

            # Mostrar el stock sumado y rango de precios en etiquetas (o inputs)
            self.stock.setValue(total_stock)
            self.stock.setDisabled(True)
            self.stock_low_input.setDisabled(True)
            self.price_input.setDisabled(True)

            # En lugar de poner un precio numérico editable, mostramos un label con el rango
            if not hasattr(self, 'price_range_label'):
                self.price_range_label = QLabel()
                self.layout().addWidget(self.price_range_label)
            self.price_range_label.setText(f"Rango de precio: ${min_price:.2f} - ${max_price:.2f}")
            self.price_range_label.show()

        else:
            # No hay variantes: habilitar inputs y esconder label rango precio si existe
            self.stock.setDisabled(False)
            self.stock_low_input.setDisabled(False)
            self.price_input.setDisabled(False)
            if hasattr(self, 'price_range_label'):
                self.price_range_label.hide()