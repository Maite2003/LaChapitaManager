from copy import deepcopy
from functools import partial

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QToolButton
)
from PySide6.QtCore import Qt, QDate

from services.product_services import ProductService
from services.transactions_services import TransactionsService
from services.agenda_services import AgendaService
from .sale_dialog import AddSaleDialog


class SalesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        # Load initial data
        self.reset_filters()
        self.load_filtered_sales()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Total product
        self.total_label = QLabel("Total ventas: 0")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.total_label)

        # --- Filters ---
        filter_layout = QHBoxLayout()

        # Add sale button
        self.add_sale_btn = QPushButton("Nueva")
        self.add_sale_btn.clicked.connect(self.open_add_sale_dialog)

        # Delete sale
        self.delete_sale_btn = QPushButton("Eliminar")
        self.delete_sale_btn.setEnabled(False)  # Initially disabled, will be enabled when a sale is selected
        self.delete_sale_btn.clicked.connect(self.delete_selected_sales)

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

        # Client
        filter_layout.addWidget(QLabel("Cliente:"))
        self.client_filter = QComboBox()
        filter_layout.addWidget(self.client_filter)

        # Connect filters
        self.date_from.dateChanged.connect(self.load_filtered_sales)
        self.date_to.dateChanged.connect(self.load_filtered_sales)
        self.min_amount.valueChanged.connect(self.load_filtered_sales)
        self.max_amount.valueChanged.connect(self.load_filtered_sales)
        self.client_filter.currentIndexChanged.connect(self.load_filtered_sales)

        filter_layout.addWidget(self.add_sale_btn)
        filter_layout.addWidget(self.delete_sale_btn)
        main_layout.addLayout(filter_layout)

        # --- Sales table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # ID (hidden), date, client, total, details button
        self.table.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Monto", "      "])
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
        clients = AgendaService.get_all_clients()
        self.client_filter.addItem("Todos", None)
        for client in clients:
            self.client_filter.addItem(f"{client['name']} {client['surname']}", client["id"])

        self.date_to.setDate(QDate.currentDate())
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # Default to one month ago

    def update_delete_button_state(self):
        selected_items = self.table.selectedItems()
        self.delete_sale_btn.setEnabled(bool(selected_items))

    def delete_selected_sales(self):
        selected_items = self.table.selectionModel().selectedRows()
        for row in selected_items:
            # Get the sale ID from the first column
            x = self.table.item(row.row(), 0)
            sale_id = x.text() if x else None
            TransactionsService.delete_sale(int(sale_id))
        self.load_filtered_sales()

    def load_filtered_sales(self):
        def get_filtered_products():
            date_from = self.date_from.date().toPython()
            date_to = self.date_to.date().toPython()
            min_amount = self.min_amount.value()
            max_amount = self.max_amount.value()
            client = self.client_filter.currentData()

            sales = TransactionsService.get_all_sales()

            # Filter sales based on criteria
            filtered_sales = []
            for s in sales:
                f = s["date"]
                f_date = QDate.fromString(f, "dd-MM-yyyy").toPython()
                if not (date_from <= f_date <= date_to):
                    continue
                if not (min_amount <= s["total"] <= max_amount):
                    continue
                if client != None and s["client_id"] != client:
                    continue
                filtered_sales.append(s)
            return filtered_sales

        filtered_sales = get_filtered_products()

        # Update total sales label
        self.total_label.setText(f"Total ventas: {len(filtered_sales)}")

        # Set up the table with filtered sales
        self.table.setRowCount(len(filtered_sales))
        for row, sale in enumerate(filtered_sales):
            client = AgendaService.get_client_by_id(sale["client_id"]) if sale["client_id"] else None

            self.table.setItem(row, 0, QTableWidgetItem(str(sale['id'])))

            # Date column
            item_fecha = QTableWidgetItem(sale["date"])
            fecha_qdate = QDate.fromString(sale["date"], "dd-MM-yyyy")
            item_fecha.setData(Qt.ItemDataRole.UserRole, fecha_qdate)
            self.table.setItem(row, 1, item_fecha)

            if client:
                self.table.setItem(row, 2, QTableWidgetItem(client["name"] + " " + client["surname"], client["id"]))
            else:
                self.table.setItem(row, 2, QTableWidgetItem("Sin cliente"))

            # Amount column
            item_amount = QTableWidgetItem(str(sale["total"]))
            self.table.setItem(row, 3, item_amount)

            # Detail buttons
            details_btn = QToolButton()
            details_btn.setText("Detalles")
            details_btn.setToolTip("Ver detalles de la venta")
            details_btn.clicked.connect(partial(self.open_add_sale_dialog, sale))
            details_btn.setStyleSheet("padding: 4px;")
            self.table.setCellWidget(row, 4, details_btn)
        self.table.selectionModel().clearSelection()  # Clear selection after saving

    def open_add_sale_dialog(self, sale=None):
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

        if not sale and len(ProductService.get_all_products(active=1)) == 0:
            return QMessageBox.warning(self, "Error", "No hay productos disponibles para agregar a la venta.")

        dialog = AddSaleDialog(self, sale)
        if dialog.exec() and dialog.result() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            sale_id =  data["id"]
            items = data["items"]
            date = data["date"]
            client_id = data["client_id"]

            if len(items) == 0:
                return QMessageBox.warning(self, "Error", "Debe agregar al menos un producto a la venta.")

            items = unify_item()
            # Check the stock is available
            available, details = self.check_stock(items=deepcopy(items), sale=sale)

            if not available:
                product_id, variant_id, quantity, stock = details
                msg = f"No hay suficiente stock para el producto {product_id} {'con variante ' + str(variant_id) if variant_id else ''}. Stock actual: {stock}, cantidad requerida: {quantity}."
                return QMessageBox.warning(self, "Error de stock", msg)
            print("Items antes del save es ", items)
            TransactionsService.save_sale(sale_id=sale_id, date=date, client_id=client_id, items=items)
            self.load_filtered_sales()

    def check_stock(self, items, sale):
        """
        Makes the difference to see how many more products were added
        """

        if sale:
            already = sale['items']
            for key, value in already.items():
                if key in items:
                    if items[key]['quantity'] != value['quantity']:
                        items[key]['quantity'] -= value['quantity'] # Shouldn't be checked for stock because it was already # checked when the sale was created
                        print("Chequear solo por ", items[key]['quantity'], " de ", key)
        return ProductService.check_stock(items=items)

    def refresh(self):
        """
        Refresh the sales page.
        """
        self.reset_filters()
        self.load_filtered_sales()