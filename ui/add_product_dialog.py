from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QDialog, QDoubleSpinBox, QPushButton, QMessageBox
)
from models.product import Product
import models.category as Category

class AddProductDialog(QDialog):
    def __init__(self, id=None, parent=None):
        super().__init__(parent)
        self.product = id

        self.setup_ui()

        if self.product:
            self.populate_fields()

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
        layout.addWidget(QLabel("Unidad (ej. kg, l, u):"))
        self.unit_input = QLineEdit()
        layout.addWidget(self.unit_input)

        # Categoría
        layout.addWidget(QLabel("Categoría:"))
        self.category_combo = QComboBox()
        self.load_categories()
        layout.addWidget(self.category_combo)

        # Precio de venta
        layout.addWidget(QLabel("Precio de venta:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.01)
        self.price_input.setMaximum(999999)
        self.price_input.setValue(1.0)
        layout.addWidget(self.price_input)

        layout.addWidget(QLabel("Stock inicial (opcional):"))
        self.stock = QDoubleSpinBox()
        self.stock.setMinimum(0.0)  # Permite 0
        self.stock.setMaximum(999999)
        self.stock.setValue(0.0)  # Por defecto 0 = sin límite
        layout.addWidget(self.stock)

        layout.addWidget(QLabel("Stock mínimo (opcional):"))
        self.stock_low_input = QDoubleSpinBox()
        self.stock_low_input.setMinimum(0.0)  # Permite 0
        self.stock_low_input.setMaximum(999999)
        self.stock_low_input.setValue(0.0)  # Por defecto 0 = sin límite
        layout.addWidget(self.stock_low_input)

        # Botones
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.save_product)
        btn_layout.addWidget(self.save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def populate_fields(self):
        product_data = Product.get_by_id(self.product)
        if not product_data:
            return QMessageBox.warning(self, "Error", "Producto no encontrado.")

        self.name_input.setText(product_data["name"])
        self.unit_input.setText(product_data["unit"])
        self.category_combo.setCurrentIndex(self.category_combo.findData(product_data["category"]))
        self.price_input.setValue(product_data["price"])
        self.stock.setValue(product_data["stock"])
        self.stock_low_input.setValue(product_data["stock_low"])

    def load_categories(self):
        for cat in Category.get_all():
            self.category_combo.addItem(cat["name"], cat["id"])

    def save_product(self):
        title = self.name_input.text().strip()
        unit = self.unit_input.text().strip()
        category_id = self.category_combo.currentData()
        price = self.price_input.value()
        stock_low = self.stock_low_input.value()
        stock = self.stock.value()
        if stock_low < 0:
            return QMessageBox.warning(self, "Error", "El stock mínimo no puede ser negativo.")
        if stock < 0:
            return QMessageBox.warning(self, "Error", "El stock no puede ser negativo.")

        if not title or not unit:
            return QMessageBox.warning(self, "Error", "Completa todos los campos.")

        if not self.product and Product.exists_with_title(title):
            return QMessageBox.warning(self, "Error", "Ya existe un producto con ese nombre.")

        try:
            if self.product:
                Product.update_product(
                    self.product, title, unit, category_id, price, stock_low, stock
                )
            else:
                Product(
                    name=title,
                    unit=unit,
                    category=category_id,
                    price=price,
                    stock=stock,
                    stock_low=stock_low
                ).save()
                QMessageBox.information(self, "Éxito", "Producto agregado con éxito.")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el producto:\n{str(e)}")
