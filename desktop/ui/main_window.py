import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QMessageBox
from PySide6.QtCore import Qt, QSettings

from .backup_dialog import BackupDialog
from .backup_toggle import DriveBackupToggle
from .clients_page import ClientsPage
from .home_page import HomePage
from .suppliers_page import SuppliersPage
from .categories_page import CategoriesPage
from .inventory_page import InventoryPage
from .purchases_page import PurchasesPage
from .sales_page import SalesPage

from utils import config
from utils.backup import make_backup, authenticate_drive
from utils.path_utils import resource_path, get_writable_path


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        if config.backup_drive: authenticate_drive()

        self.setWindowTitle("LaChapita Manager")
        logo_path = resource_path("assets/logo.png")
        self.setWindowIcon(QIcon(logo_path))
        self.resize(800, 600)

        # Buttons style
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

        # Nav buttons list
        self.nav_btns = []

        # Main layout
        main_layout = QHBoxLayout(self)

        # Sidebar navigation widget
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setStyleSheet("background-color: #2e2b32;")

        sidebar = QVBoxLayout(self.sidebar_widget)
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        logo_label = QLabel()
        logo_label.setPixmap(QIcon(logo_path).pixmap(100, 100))
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
        sidebar.addStretch()

        self.backup_toggle = DriveBackupToggle(
            checked=config.backup_drive,
            on_toggle=self.handle_drive_backup_toggle
        )
        self.nav_btns.append(self.backup_toggle)
        self.backup_btn = QPushButton("Backup")
        self.nav_btns.append(self.backup_btn)

        self.backup_toggle.setStyleSheet(button_style)
        sidebar.addWidget(self.backup_toggle)

        self.backup_btn.setStyleSheet(button_style)
        self.backup_btn.setCheckable(True)
        sidebar.addWidget(self.backup_btn)


        # Content area

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

        # Connect buttons to stack changes
        main_buttons = self.nav_btns[:-2]  # Exclude the backup toggle and backup button
        self.home_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(0), self.activate_button(self.home_btn, main_buttons)))
        self.inventory_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(1), self.activate_button(self.inventory_btn, main_buttons)))
        self.sales_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(2), self.activate_button(self.sales_btn, main_buttons)))
        self.purchases_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(3), self.activate_button(self.purchases_btn, main_buttons)))
        self.clients_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(4), self.activate_button(self.clients_btn, main_buttons)))
        self.suppliers_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(5), self.activate_button(self.suppliers_btn, main_buttons)))
        self.categories_btn.clicked.connect(lambda: (self.stack.setCurrentIndex(6), self.activate_button(self.categories_btn, main_buttons)))
        self.backup_btn.clicked.connect(lambda: self.on_backup_btn_clicked())

        # Activate the home button and set the initial page
        self.activate_button(self.home_btn, main_buttons)
        self.stack.setCurrentIndex(0)
        self.on_page_changed(0)

        # Add widgets to the main layout
        main_layout.addWidget(self.sidebar_widget, 1)
        main_layout.addWidget(self.stack, 4)

        # Signal connections for refreshing pages
        self.inventory_page.product_changed.connect(self.categories_page.refresh)

    def handle_drive_backup_toggle(self, enabled: bool):
        """
        Handle the toggle state of the Drive Backup.
        If enabled, authenticate and set the backup_drive to True.
        If disabled, set the backup_drive to False.
        """
        settings_path = os.path.join(get_writable_path(), "lachapita_config.ini")
        settings = QSettings(settings_path, QSettings.Format.IniFormat)
        print("Drive Backup toggle changed to: ", enabled)
        if enabled:
            print("Drive Backup enabled.")
            authenticated, msg = authenticate_drive()
            if not authenticated:
                self.backup_toggle.set_checked(False)
                config.backup_drive = False
                settings.setValue("backup_drive_enabled", False)

                # Display error message
                QMessageBox.warning(self, "Error de autenticación", msg)

            else:
                config.backup_drive = True
                settings.setValue("backup_drive_enabled", True)
                print("Drive Backup enabled and authenticated.")
        else:
            config.backup_drive = False
            settings.setValue("backup_drive_enabled", False)
            print("Drive Backup disabled.")

    def closeEvent(self, event):
        """
        Override close event make a backup before closing the window.
        """
        make_backup()
        event.accept()

    def on_page_changed(self, index):
        current_page = self.stack.widget(index)
        # Intentar llamar a refresh si existe el método
        if hasattr(current_page, "refresh"):
            current_page.refresh()

    def activate_button(self, active_btn, btns):
        for btn in btns:
            btn.setChecked(btn == active_btn)

    def on_backup_btn_clicked(self):
        """
        Handle the backup button click.
        """
        dialog = BackupDialog()
        dialog.exec()

        # After changing the db, refresh the pages
        self.home_page.refresh()
        self.inventory_page.refresh()
        self.sales_page.refresh()
        self.purchases_page.refresh()
        self.clients_page.refresh()
        self.suppliers_page.refresh()
        self.categories_page.refresh()

        # Reset to home page
        self.backup_btn.setChecked(False)
        self.stack.setCurrentIndex(0)
        self.activate_button(self.home_btn, self.nav_btns[:-2])  # Exclude the backup toggle and backup button
