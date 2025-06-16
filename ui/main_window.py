from itertools import product

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PySide6.QtCore import Qt
from ui.sales_page import SalesPage
from ui.purchases_page import PurchasesPage
from ui.inventory_page import InventoryPage
from ui.clients_page import ClientsPage
from ui.suppliers_page import SuppliersPage
from ui.categories_page import CategoriesPage

from ui.inventory_page import InventoryPage
from ui.purchases_page import PurchasesPage
from ui.sales_page import SalesPage

from models.product import Product
from models.client import Client
import models.category as Category

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaChapita Manager")
        self.resize(800, 600)

        # Estilo de botones
        button_style = """
        QPushButton {
            background-color: #2e2b32;
            color: white;
            border: none;
            padding: 12px 20px;
            text-align: left;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #827369;
        }
        QPushButton:checked {
            background-color: #faa22d;
            color: #000000;
            font-weight: bold;
        }
        """

        # Botones de navegación
        self.nav_btns = []

        # Layout principal horizontal
        main_layout = QHBoxLayout(self)

        # Barra lateral
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setStyleSheet("background-color: #2e2b32;")

        sidebar = QVBoxLayout(self.sidebar_widget)
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.inventory_btn = QPushButton("Inventario")
        self.nav_btns.append(self.inventory_btn)
        self.sales_btn = QPushButton("Ventas")
        self.nav_btns.append(self.sales_btn)
        self.purchases_btn = QPushButton("Compras")
        self.nav_btns.append(self.purchases_btn)
        self.clients_btn = QPushButton("Clientes")
        self.nav_btns.append(self.clients_btn)
        self.suppliers_btn = QPushButton("Proveedores")
        self.nav_btns.append(self.suppliers_btn)
        self.categories_btn = QPushButton("Categorías")
        self.nav_btns.append(self.categories_btn)

        for btn in self.nav_btns:
            btn.setStyleSheet(button_style)
            btn.setCheckable(True)
            sidebar.addWidget(btn)

        # Área de contenido (stacked widget)
        self.stack = QStackedWidget()
        self.stack.addWidget(InventoryPage())
        self.stack.addWidget(SalesPage())
        self.stack.addWidget(PurchasesPage())
        self.stack.addWidget(ClientsPage())
        self.stack.addWidget(SuppliersPage())
        self.stack.addWidget(CategoriesPage())
        self.stack.currentChanged.connect(self.on_page_changed)

        # Conectar botones con páginas
        self.inventory_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(0), self.activate_button(self.inventory_btn, self.nav_btns)))
        self.sales_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(1), self.activate_button(self.sales_btn, self.nav_btns)))
        self.purchases_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(2), self.activate_button(self.purchases_btn, self.nav_btns)))
        self.clients_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(3), self.activate_button(self.clients_btn, self.nav_btns)))
        self.suppliers_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(4), self.activate_button(self.suppliers_btn, self.nav_btns)))
        self.categories_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(5), self.activate_button(self.categories_btn, self.nav_btns)))

        # Activar el botón de inventario por defecto
        self.activate_button(self.inventory_btn, self.nav_btns)
        self.stack.setCurrentIndex(0)

        # Agregar al layout principal
        main_layout.addWidget(self.sidebar_widget, 1)
        main_layout.addWidget(self.stack, 4)

    def on_page_changed(self, index):
        current_page = self.stack.widget(index)
        # Intentar llamar a refresh si existe el método
        if hasattr(current_page, "refresh"):
            current_page.refresh()

    def activate_button(self, active_btn, btns):
        for btn in btns:
            btn.setChecked(btn == active_btn)
