from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QHBoxLayout, QPushButton


class VariantDialog(QDialog):
    def __init__(self, parent=None, variant_data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar variante" if variant_data else "Agregar variante")
        self.variant_data = variant_data or {}
        self.setup_ui()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Nombre de variante:"))
        self.variant_name_input = QLineEdit()
        if self.variant_data:
            self.variant_name_input.setText(self.variant_data.get('variant_name', ''))
        layout.addWidget(self.variant_name_input)

        layout.addWidget(QLabel("Stock:"))
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setMaximum(999999)
        if self.variant_data:
            self.stock_input.setValue(self.variant_data.get('stock', 0))
        layout.addWidget(self.stock_input)

        layout.addWidget(QLabel("Stock Minimo:"))
        self.stock_low_input = QDoubleSpinBox()
        self.stock_low_input.setMaximum(999999)
        if self.variant_data:
            self.stock_low_input.setValue(self.variant_data.get('stock_low', 0))
        layout.addWidget(self.stock_low_input)

        layout.addWidget(QLabel("Precio:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999)
        self.price_input.setDecimals(2)
        if self.variant_data:
            self.price_input.setValue(self.variant_data.get('price', 0))
        layout.addWidget(self.price_input)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        if self.variant_data:
            self.variant_data['variant_name'] = self.variant_name_input.text()
            self.variant_data['stock'] = self.stock_input.value()
            self.variant_data['stock_low'] = self.stock_low_input.value()
            self.variant_data['price'] = self.price_input.value()
            return self.variant_data
        return {
            'variant_name': self.variant_name_input.text(),
            'stock': self.stock_input.value(),
            'stock_low': self.stock_low_input.value(),
            'price': self.price_input.value()
        }