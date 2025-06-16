from functools import partial

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView
)
from PySide6.QtCore import Qt
from models.product import Product
import models.category as Category
from ui.add_product_dialog import AddProductDialog


class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # Label total productos
        self.total_label = QLabel("Total productos: 0")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.total_label)

        # Layout para búsqueda y filtros
        filters_layout = QHBoxLayout()

        self.add_product_btn = QPushButton("Agregar producto")
        self.add_product_btn.clicked.connect(self.open_add_product_dialog)
        filters_layout.addWidget(self.add_product_btn)

        # Barra de búsqueda
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar por título...")
        filters_layout.addWidget(self.search_bar, 3)  # peso 3 para que sea más ancho

        # ComboBox para categorías
        self.category_filter = QComboBox()
        filters_layout.addWidget(self.category_filter, 2)

        # Checkbox Bajo stock
        self.low_stock_cb = QCheckBox("Bajo stock")
        filters_layout.addWidget(self.low_stock_cb)

        # Checkbox Sin stock
        self.no_stock_cb = QCheckBox("Sin stock")
        filters_layout.addWidget(self.no_stock_cb)

        main_layout.addLayout(filters_layout)

        # Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Id (hidden), Name, Category, Stock, Edit button
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Categoría", "Stock", " "])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.hideColumn(0)  # Ocultar columna de ID
        header = self.table.horizontalHeader()

        # Estirar las primeras 3 columnas (Nombre, Categoría, Stock)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Hacer que la columna de botón ("Editar") se ajuste al contenido
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        main_layout.addWidget(self.table)

        # Lista de productos cargados (se asigna con load_products)
        self.load_products()

        # Conectar filtros para refrescar tabla
        self.search_bar.textChanged.connect(self.filter_products)
        self.category_filter.currentIndexChanged.connect(self.filter_products)
        self.low_stock_cb.stateChanged.connect(self.filter_products)
        self.no_stock_cb.stateChanged.connect(self.filter_products)

        # Mostrar datos iniciales
        self.filter_products()

    def load_products(self):
        self.products = Product.get_all()

        # Limpiar combo y volver a llenar
        self.category_filter.blockSignals(True)  # bloquear señal para evitar refresh prematuro
        self.category_filter.clear()
        self.category_filter.addItem("Todas las categorías")
        categories = sorted(c['name'] for c in Category.get_all())
        self.category_filter.addItems(categories)
        self.category_filter.blockSignals(False)

        # Aplicar filtro y actualizar tabla
        self.filter_products()

    def filter_products(self):
        text = self.search_bar.text().lower()
        category = self.category_filter.currentText()
        low_stock = self.low_stock_cb.isChecked()
        no_stock = self.no_stock_cb.isChecked()

        filtered = []
        for p in self.products:
            if text and text not in p["name"].lower():
                continue
            if category != "Todas las categorías" and p["category"] != category:
                continue
            if low_stock and p["stock"] < p["low_stock"]:
                continue
            if no_stock and p["stock"] == 0:
                continue
            filtered.append(p)

        # Actualizar total
        self.total_label.setText(f"Total productos: {len(filtered)}")

        # Actualizar tabla
        self.table.setRowCount(len(filtered))
        for row, product in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(product["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(product["category"]))
            stock_item = QTableWidgetItem(str(product["stock"]))
            # Opcional: mostrar stock en rojo si 0
            if product["stock"] == 0:
                stock_item.setForeground(Qt.GlobalColor.red)
            elif product["stock"] <= product["stock_low"]:
                stock_item.setForeground(Qt.GlobalColor.darkYellow)
            else:
                stock_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 3, stock_item)
            # Botón de Detalles
            details_btn = QPushButton("Editar")
            details_btn.clicked.connect(partial(self.show_product_details, product['id']))
            details_btn.setStyleSheet("padding: 4px;")
            self.table.setCellWidget(row, 4, details_btn)

            self.table.setColumnHidden(0, True)  # Ocultamos el ID
            header = self.table.horizontalHeader()

            # Estirar las primeras 3 columnas (Nombre, Categoría, Stock)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

            # Hacer que la columna de botón ("Editar") se ajuste al contenido
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

    def refresh(self):
        """
        Refresca la lista de productos y actualiza la tabla.
        """
        self.load_products()

    def open_add_product_dialog(self):
        dialog = AddProductDialog(parent=self)
        if dialog.exec():
            self.load_products()  # Recargar la lista o tabla de productos

    def show_product_details(self, product_id):
        dialog = AddProductDialog(id=product_id, parent=self)
        dialog.exec()