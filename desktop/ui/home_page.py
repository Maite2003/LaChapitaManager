from PySide6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, \
    QHeaderView, QScrollArea
from services.agenda_services import AgendaService
from services.product_services import ProductService
from services.transactions_services import TransactionsService
from desktop.ui.category_progress import SalesCategoryProgress
from utils.periods import PERIODS, get_period_range


def get_data(start_date, end_date):
    sales_total, purchases_total = TransactionsService.get_totals(start_date, end_date)
    top5_products = TransactionsService.get_top5_products(start_date=start_date, end_date=end_date)
    last_sales = TransactionsService.get_all_sales(start_date=start_date, end_date=end_date)#.reverse()
    last_purchases = TransactionsService.get_all_purchases(start_date=start_date, end_date=end_date)#.reverse()
    low_stock = ProductService.get_low_stock()

    return sales_total, purchases_total, last_sales, last_purchases, top5_products, low_stock


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Period selector
        self.period_combo = QComboBox()
        for period,id in PERIODS.items():
            self.period_combo.addItem(period, id)
        self.period_combo.setCurrentIndex(0) # By default, last week
        self.period_combo.currentIndexChanged.connect(self.refresh)

        layout.addWidget(self.period_combo)

        main_layout = QHBoxLayout()
        layout.addLayout(main_layout)

        # Sales
        sales_layout = QVBoxLayout()

        # Total
        total_sales = QHBoxLayout()
        self.total_sales = QLabel("Ventas totales: $0.00")
        self.total_sales.setStyleSheet("font-weight: bold; font-size: 16px;")
        total_sales.addWidget(self.total_sales)
        sales_layout.addLayout(total_sales)

        # Last sales
        self.last_sales_table = QTableWidget()
        self.last_sales_table.setColumnCount(3)
        self.last_sales_table.setHorizontalHeaderLabels(["Fecha", "Cliente", "Total"])
        self.last_sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Make it read-only
        self.last_sales_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)  # Disable selection
        header = self.last_sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        sales_layout.addWidget(self.last_sales_table)

        # Top 5 products label
        top5 = QLabel("Productos mas vendidos")
        top5.setStyleSheet("font-weight: bold; font-size: 16px;")
        sales_layout.addWidget(top5)

        # Top 5 Products table
        self.top5_table = QTableWidget()
        self.top5_table.setColumnCount(3)
        self.top5_table.setHorizontalHeaderLabels(["Producto", "Variante", "Cantidad"])
        self.top5_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make it read-only
        self.top5_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        header = self.top5_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        sales_layout.addWidget(self.top5_table)

        # Purchases
        purchases_layout = QVBoxLayout()

        # Total
        total_purchases = QHBoxLayout()
        self.total_purchases = QLabel("Compras totales: $0.00")
        self.total_purchases.setStyleSheet("font-weight: bold; font-size: 16px;")
        total_purchases.addWidget(self.total_purchases)
        purchases_layout.addLayout(total_purchases)

        # Last purchases
        self.last_purchases_table = QTableWidget()
        self.last_purchases_table.setColumnCount(3)
        self.last_purchases_table.setHorizontalHeaderLabels(["Fecha", "Proveedor", "Total"])
        self.last_purchases_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make it read-only
        self.last_purchases_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)  # Disable selection
        purchases_layout.addWidget(self.last_purchases_table)
        header = self.last_purchases_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Low stock / out of stock label
        self.low = QLabel("Productos con bajo stock: 0")
        self.low.setStyleSheet("font-weight: bold; font-size: 16px;")
        purchases_layout.addWidget(self.low)

        # Low stock / Out of stock table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(4)
        self.low_stock_table.setHorizontalHeaderLabels(["Producto", "Variante", "Stock Minimo", "Stock actual"])
        header = self.low_stock_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        purchases_layout.addWidget(self.low_stock_table)

        # Progress bar that shows the sales by categories
        self.categories_progress = SalesCategoryProgress()

        # ScrollArea that contains the categories progress bar
        self.categories_scroll = QScrollArea()
        self.categories_scroll.setWidgetResizable(True)
        self.categories_scroll.setWidget(self.categories_progress)

        main_layout.addLayout(sales_layout)
        main_layout.addLayout(purchases_layout)
        layout.addWidget(self.categories_scroll)

    def table_heigt(self, table, rows):
        """
        Set the height of a table based on the number of rows and the height of the first row.
        """
        if table.rowCount() == 0:
            row_height = 30
        else:
            row_height = table.rowHeight(0)

        total_height = (row_height * rows) + table.horizontalHeader().height() + 2
        table.setFixedHeight(total_height)

    def refresh(self):
        period = self.period_combo.currentText()
        start_date, end_date = get_period_range(period)

        sales_total, purchases_total, sales, purchases, top5, low_stock = get_data(start_date, end_date)

        self.categories_progress.set_data(TransactionsService.get_sales_by_categories(start_date, end_date), ProductService.get_all_categories())

        self.load_sales(sales, sales_total, top5)
        self.load_purchases(purchases, purchases_total, low_stock)

    def load_sales(self, sales, sales_total, top5):
        # Update total sales
        self.total_sales.setText(f"Ventas totales: ${sales_total:.2f} ({len(sales)} ventas)")

        # Update last sales table
        self.last_sales_table.setRowCount(len(sales))
        if sales:
            sales = sales[:5]
            for i, sale in enumerate(sales):
                self.last_sales_table.setItem(i, 0, QTableWidgetItem(sale["date"]))
                client = AgendaService.get_client_by_id(sale["client_id"])
                if client:
                    self.last_sales_table.setItem(i, 1, QTableWidgetItem(client["name"] + " " + client["surname"]))
                else:
                    self.last_sales_table.setItem(i, 1, QTableWidgetItem("-"))
                self.last_sales_table.setItem(i, 2, QTableWidgetItem(f"${sale['total']:.2f}"))
        self.table_heigt(self.last_sales_table, 5)

        # Update top 5 products table
        self.top5_table.setRowCount(len(top5))
        for i, product in enumerate(top5):
            self.top5_table.setItem(i, 0, QTableWidgetItem(product[0]))
            if not product[1]:
                self.top5_table.setItem(i, 1, QTableWidgetItem('-'))
            else:
                self.top5_table.setItem(i, 1, QTableWidgetItem(product[1]))
            self.top5_table.setItem(i, 2, QTableWidgetItem(str(product[2])))
        self.table_heigt(self.top5_table, 5)

    def load_purchases(self, purchases, purchases_total, low_stock):
        self.total_purchases.setText(f"Compras totales: ${purchases_total:.2f} ({len(purchases)} compras)")

        # Update last purchases table
        self.last_purchases_table.setRowCount(len(purchases))
        if purchases:
            purchases = purchases[:5]
            for i, purchase in enumerate(purchases):
                self.last_purchases_table.setItem(i, 0, QTableWidgetItem(purchase["date"]))
                supplier = AgendaService.get_supplier_by_id(purchase["supplier_id"])
                if supplier:
                    self.last_purchases_table.setItem(i, 1, QTableWidgetItem(supplier["name"] + " " + supplier["surname"]))
                else:
                    self.last_purchases_table.setItem(i, 1, QTableWidgetItem("-"))
                self.last_purchases_table.setItem(i, 2, QTableWidgetItem(f"${purchase['total']:.2f}"))
        self.table_heigt(self.last_purchases_table, 5)

        # Update low stock table
        self.low.setText(f"Productos con bajo stock: {len(low_stock)}")
        low_stock = low_stock[:5]  # Show only the first 5 products with low stock
        self.low_stock_table.setRowCount(len(low_stock))
        for i, product in enumerate(low_stock):
            self.low_stock_table.setItem(i, 0, QTableWidgetItem(product["product_name"]))
            if not product['variant_name']:
                self.low_stock_table.setItem(i, 1, QTableWidgetItem('-'))
            else:
                self.low_stock_table.setItem(i, 1, QTableWidgetItem(product["variant_name"]))
            self.low_stock_table.setItem(i, 2, QTableWidgetItem(str(product["low_stock"])))
            self.low_stock_table.setItem(i, 3, QTableWidgetItem(str(product["stock"])))
        self.table_heigt(self.low_stock_table, 5)
