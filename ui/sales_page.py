from functools import partial

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QDate

from models.client import Client
from ui.sale_dialog import AddSaleDialog
from ui.sale_detail_dialog import SaleDetailDialog

import models.sale as Sale


class SalesPage(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # --- Filtros ---
        filter_layout = QHBoxLayout()

        self.add_sale_btn = QPushButton("Agregar venta")
        self.add_sale_btn.clicked.connect(self.open_add_sale_dialog)

        # Fecha desde
        filter_layout.addWidget(QLabel("Fecha desde:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # Por defecto hace 1 mes atrás
        filter_layout.addWidget(self.date_from)

        # Fecha hasta
        filter_layout.addWidget(QLabel("Fecha hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to)

        # Monto mínimo
        filter_layout.addWidget(QLabel("Monto mínimo:"))
        self.min_amount = QDoubleSpinBox()
        self.min_amount.setRange(0, 1000000)
        filter_layout.addWidget(self.min_amount)

        # Monto máximo
        filter_layout.addWidget(QLabel("Monto máximo:"))
        self.max_amount = QDoubleSpinBox()
        self.max_amount.setRange(0, 1000000)
        self.max_amount.setValue(1000000)
        filter_layout.addWidget(self.max_amount)

        # Cliente
        filter_layout.addWidget(QLabel("Cliente:"))
        self.client_filter = QComboBox()
        self.client_filter.addItem("Todos")
        # Aquí deberías cargar clientes de la base
        filter_layout.addWidget(self.client_filter)

        # Botón aplicar filtros
        self.apply_filters_btn = QPushButton("Aplicar filtros")
        filter_layout.addWidget(self.apply_filters_btn)
        filter_layout.addWidget(self.add_sale_btn)
        main_layout.addLayout(filter_layout)

        # --- Tabla de ventas ---
        self.table = QTableWidget()
        self.table.setColumnCount(5) # ID (hidden), date, client, total, details button
        self.table.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Monto", "      "])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        header = self.table.horizontalHeader()

        # Estirar las primeras 3 columnas
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Hacer que la columna de botón se ajuste al contenido
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        main_layout.addWidget(self.table)

        # Conectar botón aplicar filtros
        self.apply_filters_btn.clicked.connect(self.load_filtered_sales)

        # Cargar datos iniciales
        self.load_clients()
        self.load_filtered_sales()

    def load_clients(self):
        # Aquí cargás clientes desde la DB, ejemplo:
        clients = Client.get_all()
        self.client_filter.addItems(clients)

    def load_filtered_sales(self):
        # Obtener valores de filtros
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        min_amount = self.min_amount.value()
        max_amount = self.max_amount.value()
        client = self.client_filter.currentText()

        # Aquí deberías hacer la consulta filtrada a la base de datos.
        # Por ahora simulo con datos ficticios:
        sales = Sale.get_all()

        # Filtrar ventas (solo ejemplo con filtros básicos)
        filtered_sales = []
        for s in sales:
            f = s["date"]
            f_date = QDate.fromString(f, "yyyy-MM-dd").toPython()
            if not (date_from <= f_date <= date_to):
                continue
            if not (min_amount <= s["total"] <= max_amount):
                continue
            if client != "Todos" and s["client"] != client:
                continue
            filtered_sales.append(s)

        def on_sale_clicked(self, row, column):
            item = self.table.item(row, 0)
            if item:
                sale_id = item.data(Qt.ItemDataRole.UserRole)
                dialog = SaleDetailDialog(sale_id, self)
                dialog.exec()

        # Mostrar en tabla
        self.table.setRowCount(len(filtered_sales))
        for row, sale in enumerate(filtered_sales):
            self.table.setItem(row, 0, QTableWidgetItem(str(sale['id'])))

            # Columna Fecha
            item_fecha = QTableWidgetItem(sale["date"])
            fecha_qdate = QDate.fromString(sale["date"], "yyyy-MM-dd")
            item_fecha.setData(Qt.UserRole, fecha_qdate)  # Para ordenar correctamente
            self.table.setItem(row, 1, item_fecha)

            self.table.setItem(row, 2, QTableWidgetItem(sale["client"]))

            # Columna Monto
            item_monto = QTableWidgetItem(str(sale["total"]))
            item_monto.setData(Qt.UserRole, sale["total"])  # Ordenar como número
            self.table.setItem(row, 3, item_monto)

            # Botón de Detalles
            details_btn = QPushButton("Detalles")
            details_btn.clicked.connect(partial(self.show_sale_details, sale['id']))
            details_btn.setStyleSheet("padding: 4px;")
            self.table.setCellWidget(row, 4, details_btn)

        self.table.setColumnHidden(0, True)  # Ocultamos el ID
        header = self.table.horizontalHeader()

        # Estirar las primeras 3 columnas
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Hacer que la columna de botón se ajuste al contenido
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)


    def show_sale_details(self, sale_id):
        dialog = SaleDetailDialog(sale_id, self)
        dialog.exec()

    def open_add_sale_dialog(self):
        dialog = AddSaleDialog(self)
        if dialog.exec() and dialog.result() == QDialog.Accepted:
            data = dialog.get_data()

            details = data.get('details', [])
            date = data.get('date')
            client_id = data.get('client_id')

            if not data or data == []:
                return QMessageBox.warning(self, "Error", "Agrega al menos un producto.")

            Sale.save_sale(date=date, client=client_id, items=details)
            self.load_filtered_sales()