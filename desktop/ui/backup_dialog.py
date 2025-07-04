from datetime import datetime

from PySide6.QtWidgets import QTableWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QMessageBox, QHeaderView

from utils.backup import get_backups, restore_backup


class BackupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restaurar Backup")
        self.resize(600, 400)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Id", "Archivo", "Fecha", "Hora"])
        self.table.setColumnHidden(0, True)  # Hide the ID column
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.btn_restore = QPushButton("Aplicar Backup")
        self.btn_restore.clicked.connect(self.confirm_and_restore)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_restore)
        button_layout.addWidget(self.btn_cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_backups()


    def load_backups(self):
            self.table.setRowCount(0)
            backups = get_backups()

            for backup in backups[0]:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(backup['id']))
                self.table.setItem(row_position, 1, QTableWidgetItem(backup['title']))
                self.table.setItem(row_position, 2, QTableWidgetItem(datetime.strftime(backup['date'], "%d/%m/%Y")))
                self.table.setItem(row_position, 3, QTableWidgetItem(backup['time'].strftime("%H:%M:%S")))

    def confirm_and_restore(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return
        filename = self.table.item(selected_row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Confirmar restauración",
            f"¿Seguro que querés restaurar el backup '{filename}'?\nEsto sobrescribirá los datos actuales.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            file_id = self.table.item(selected_row, 0).text()
            restore_backup(file_id)
            QMessageBox.information(self, "Restaurado", "Backup restaurado correctamente.")
            self.accept()

