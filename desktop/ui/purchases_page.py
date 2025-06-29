from functools import partial

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QToolButton
)
from PySide6.QtCore import Qt, QDate

from core.product_services import ProductService
from core.transactions_services import TransactionsService
from core.agenda_services import AgendaService
from desktop.ui.purchase_dialog import PurchaseDialog


class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        # Load initial data
        self.reset_filters()
        self.load_filtered_purchases()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Total product
        self.total_label = QLabel("Total compras: 0")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.total_label)

        # --- Filters ---
        filter_layout = QHBoxLayout()

        # Add sale button
        self.add_purchase_btn = QPushButton("Nueva")
        self.add_purchase_btn.clicked.connect(self.open_purchase_dialog)

        # Delete sale
        self.delete_purchase_btn = QPushButton("Eliminar")
        self.delete_purchase_btn.setEnabled(False)  # Initially disabled, will be enabled when a sale is selected
        self.delete_purchase_btn.clicked.connect(self.delete_selected_sales)

        # Date since
        filter_layout.addWidget(QLabel("Fecha desde:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # By default, one month ago
        self.date_from.setMaximumDate(QDate.currentDate())  # Don't allow future dates
        filter_layout.addWidget(self.date_from)

        # Date until
        filter_layout.addWidget(QLabel("Fecha hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate()) # By default, today
        self.date_to.setMaximumDate(QDate.currentDate())  # Don't allow future dates
        filter_layout.addWidget(self.date_to)

        # Amount minimum
        filter_layout.addWidget(QLabel("Monto mínimo:"))
        self.min_amount = QDoubleSpinBox()
        self.min_amount.setRange(0, 1000000)
        filter_layout.addWidget(self.min_amount)

        # Amount maximum
        filter_layout.addWidget(QLabel("Monto máximo:"))
        self.max_amount = QDoubleSpinBox()
        self.max_amount.setRange(0, 1000000)
        self.max_amount.setValue(1000000)
        filter_layout.addWidget(self.max_amount)

        # Supplier
        filter_layout.addWidget(QLabel("Proveedor:"))
        self.supplier_filter = QComboBox()
        filter_layout.addWidget(self.supplier_filter)

        # Connect filters
        self.date_from.dateChanged.connect(self.load_filtered_purchases)
        self.date_to.dateChanged.connect(self.load_filtered_purchases)
        self.min_amount.valueChanged.connect(self.load_filtered_purchases)
        self.max_amount.valueChanged.connect(self.load_filtered_purchases)
        self.supplier_filter.currentIndexChanged.connect(self.load_filtered_purchases)

        filter_layout.addWidget(self.add_purchase_btn)
        filter_layout.addWidget(self.delete_purchase_btn)
        main_layout.addLayout(filter_layout)

        # --- Sales table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # ID (hidden), date, supplier, total, details button
        self.table.setHorizontalHeaderLabels(["ID", "Fecha", "Proveedor", "Monto", "      "])
        self.table.setColumnHidden(0, True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.update_delete_button_state)

        # Resize cols
        header = self.table.horizontalHeader()
        # Stretch the columns 1 to 3
        for i in range(1, self.table.columnCount() - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # Make the details column fit the content
        header.setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.ResizeMode.ResizeToContents)

        main_layout.addWidget(self.table)

    def reset_filters(self):
        suppliers = AgendaService.get_all_suppliers()
        self.supplier_filter.addItem("Todos", None)
        for supplier in suppliers:
            self.supplier_filter.addItem(f"{supplier['name']} {supplier['surname']}", supplier["id"])

        self.date_to.setDate(QDate.currentDate())
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # Default to one month ago

    def update_delete_button_state(self):
        selected_items = self.table.selectedItems()
        self.delete_purchase_btn.setEnabled(bool(selected_items))

    def delete_selected_sales(self):
        selected_items = self.table.selectionModel().selectedRows()
        for row in selected_items:
            # Get the sale ID from the first column
            x = self.table.item(row.row(), 0)
            purchase_id = x.text() if x else None
            TransactionsService.delete_purchase(int(purchase_id))
        self.load_filtered_purchases()

    def load_filtered_purchases(self):
        def get_filtered_products():
            date_from = self.date_from.date().toPython()
            date_to = self.date_to.date().toPython()
            min_amount = self.min_amount.value()
            max_amount = self.max_amount.value()
            client = self.supplier_filter.currentData()

            purchases = TransactionsService.get_all_purchases()

            # Filter purchases based on criteria
            filtered_purchases = []
            for purchase in purchases:
                f = purchase["date"]
                f_date = QDate.fromString(f, "dd-MM-yyyy").toPython()
                if not (date_from <= f_date <= date_to):
                    continue
                if not (min_amount <= purchase["total"] <= max_amount):
                    continue
                if client != None and purchase["client_id"] != client:
                    continue
                filtered_purchases.append(purchase)
            return sorted(filtered_purchases, key=lambda x: QDate.fromString(x["date"], "dd-MM-yyyy"), reverse=True)

        filtered_purchase = get_filtered_products()

        # Update total purchases label
        self.total_label.setText(f"Total compras: {len(filtered_purchase)}")

        # Set up the table with filtered purchases
        self.table.setRowCount(len(filtered_purchase))
        for row, purchase in enumerate(filtered_purchase):
            supplier = AgendaService.get_supplier_by_id(purchase["supplier_id"]) if purchase["supplier_id"] else None

            self.table.setItem(row, 0, QTableWidgetItem(str(purchase['id'])))

            # Date column
            item_date = QTableWidgetItem(purchase["date"])
            date_qdate = QDate.fromString(purchase["date"], "dd-MM-yyyy")
            item_date.setData(Qt.ItemDataRole.UserRole, date_qdate)
            self.table.setItem(row, 1, item_date)

            if supplier:
                self.table.setItem(row, 2, QTableWidgetItem(supplier["name"] + " " + supplier["surname"], supplier["id"]))
            else:
                self.table.setItem(row, 2, QTableWidgetItem("Sin proveedor"))

            # Amount column
            item_amount = QTableWidgetItem(str(purchase["total"]))
            item_amount.setData(Qt.ItemDataRole.UserRole, purchase["total"])
            self.table.setItem(row, 3, item_amount)

            # Detail buttons
            details_btn = QToolButton()
            details_btn.setText("Detalles")
            details_btn.clicked.connect(partial(self.open_purchase_dialog, purchase))
            details_btn.setStyleSheet("padding: 4px;")
            self.table.setCellWidget(row, 4, details_btn)

    def open_purchase_dialog(self, purchase=None):
        def unify_item():
            """
            Changes the format of items from (product_id, variant_id, quantity, unit_price, active)
            :return: a dictionary with (product_id, variant_id) as keys and a dictionary with 'quantity', 'unit_price', and 'active' as values
            """
            actual_products = {}
            for p_id, v_id, qty, price, active in items:
                key = (p_id, v_id)
                if key in actual_products:
                    actual_products[key]['quantity'] += qty
                else:
                    actual_products[key] = {'quantity': qty, 'unit_price': price, "active": active}
            return actual_products

        opt = ProductService.get_all_products(active=1)
        if not purchase and len(opt) == 0:
            return QMessageBox.warning(self, "Error", "No hay productos activos para realizar una compra.")

        dialog = PurchaseDialog(self, purchase)
        if dialog.exec() and dialog.result() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            purchase_id =  data["id"]
            items = data["items"]
            date = data["date"]
            supplier_id = data.get("supplier_id", None)
            if len(items) == 0:
                return QMessageBox.warning(self, "Error", "Debe agregar al menos un producto a la compra.")

            items = unify_item()
            TransactionsService.save_purchase(purchase_id=purchase_id, date=date, supplier_id=supplier_id, items=items)
            self.reset_filters()
            self.load_filtered_purchases()

    def refresh(self):
        """
        Refresh the purchases page.
        """
        self.reset_filters()
        self.load_filtered_purchases()