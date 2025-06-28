import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from desktop.ui.clients_page import ClientsPage
from desktop.ui.home_page import HomePage
from desktop.ui.suppliers_page import SuppliersPage
from desktop.ui.categories_page import CategoriesPage

from desktop.ui.inventory_page import InventoryPage
from desktop.ui.purchases_page import PurchasesPage
from desktop.ui.sales_page import SalesPage


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaChapita Manager")
        IMG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "logo.png")
        self.setWindowIcon(QIcon(IMG_PATH))
        self.resize(800, 600)

        # Estilo de botones
        button_style = """
        QToolButton {
            background-color: #2e2b32;
            color: white;
            border: none;
            padding: 4px 8px;
            font-size: 14px;
        }
        QToolButton:hover {
            background-color: #827369;
        }
        QPushButton {
            background-color: #2e2b32;
            color: white;
            border: none;
            padding: 4px 8px;
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
        logo_label = QLabel()
        logo_label.setPixmap(QIcon(IMG_PATH).pixmap(100, 100))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar.addStretch()
        sidebar.addWidget(logo_label)
        sidebar.addStretch()

        self.home_btn = QPushButton("Inicio")
        self.nav_btns.append(self.home_btn)
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
        sidebar.addStretch()  # Espacio al final de la barra lateral

        # Área de contenido (stacked widget)

        self.home_page = HomePage()
        self.inventory_page = InventoryPage()
        self.sales_page = SalesPage()
        self.purchases_page = PurchasesPage()
        self.clients_page = ClientsPage()
        self.suppliers_page = SuppliersPage()
        self.categories_page = CategoriesPage()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.inventory_page)
        self.stack.addWidget(self.sales_page)
        self.stack.addWidget(self.purchases_page)
        self.stack.addWidget(self.clients_page)
        self.stack.addWidget(self.suppliers_page)
        self.stack.addWidget(self.categories_page)
        self.stack.currentChanged.connect(self.on_page_changed)

        # Conectar botones con páginas
        self.home_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(0), self.activate_button(self.home_btn, self.nav_btns)))
        self.inventory_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(1), self.activate_button(self.inventory_btn, self.nav_btns)))
        self.sales_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(2), self.activate_button(self.sales_btn, self.nav_btns)))
        self.purchases_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(3), self.activate_button(self.purchases_btn, self.nav_btns)))
        self.clients_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(4), self.activate_button(self.clients_btn, self.nav_btns)))
        self.suppliers_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(5), self.activate_button(self.suppliers_btn, self.nav_btns)))
        self.categories_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(6), self.activate_button(self.categories_btn, self.nav_btns)))

        # Activar el botón de home por defecto
        self.activate_button(self.home_btn, self.nav_btns)
        self.stack.setCurrentIndex(0)
        self.on_page_changed(0)

        # Agregar al layout principal
        main_layout.addWidget(self.sidebar_widget, 1)
        main_layout.addWidget(self.stack, 4)

        # Señales
        self.inventory_page.product_changed.connect(self.categories_page.refresh)

    def on_page_changed(self, index):
        current_page = self.stack.widget(index)
        # Intentar llamar a refresh si existe el método
        if hasattr(current_page, "refresh"):
            current_page.refresh()

    def activate_button(self, active_btn, btns):
        for btn in btns:
            btn.setChecked(btn == active_btn)
