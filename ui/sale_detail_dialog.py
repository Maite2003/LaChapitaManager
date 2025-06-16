from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QDialog
)
import models.sale as Sale

class SaleDetailDialog(QDialog):
    def __init__(self, sale_id, parent=None):
        super().__init__(parent)
        self.sale_id = sale_id
        self.setWindowTitle("Detalle de venta")
        self.setMinimumSize(500, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.sale_info_label = QLabel("Cargando datos...")
        self.layout.addWidget(self.sale_info_label)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.close_btn)

        self.load_sale_details()

    def load_sale_details(self):
        info, details = Sale.load_sale_details(self.sale_id)

        if info:
            date, name, surname, total = info
            client_str = f"{name} {surname}" if name else "Sin cliente"
            self.sale_info_label.setText(f"<b>Fecha:</b> {date} | <b>Cliente:</b> {client_str} | <b>Total:</b> ${total:.2f}")

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio unitario"])
        self.table.setRowCount(len(details))

        for row_idx, (title, quantity, unit_price) in enumerate(details):
            self.table.setItem(row_idx, 0, QTableWidgetItem(title))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(quantity)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"${unit_price:.2f}"))

        self.table.resizeColumnsToContents()
