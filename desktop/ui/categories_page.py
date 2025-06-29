from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit, QListWidget, \
    QMessageBox, QInputDialog, QTableWidget, QTableWidgetItem, QHeaderView
from core.product_services import ProductService


class CategoriesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.categories_label = QLabel("Categories: 0")
        self.categories_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.layout().addWidget(self.categories_label)

        # Category's list
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Id", "Categoría", "Cantidad de productos"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self.update_buttons_state)

        self.table.hideColumn(0)  # Hide the ID column
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.layout().addWidget(self.table)

        # New category's form
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nueva categoría")
        self.name_input.textChanged.connect(self.update_add_button_state)

        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self.handle_add_category)
        self.update_add_button_state()

        # Button for deleting selected categories
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.handle_delete_selected)

        # Button for renaming selected category
        self.rename_btn = QPushButton("Renombrar")
        self.rename_btn.setEnabled(False)
        self.rename_btn.clicked.connect(self.rename_category_dialog)

        form_layout.addWidget(self.delete_btn)
        form_layout.addWidget(self.rename_btn)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.add_btn)

        self.layout().addLayout(form_layout)

        self.load_categories()

    def load_categories(self):
        self.table.setRowCount(0)
        categories = ProductService.get_all_categories()

        # Update total products label
        self.categories_label.setText(f"Categories: {len(categories)}")

        for row, cat in enumerate(categories):
            name = cat['name']
            count = ProductService.count_products_by_category(name)

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(cat['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(str(count)))

    def handle_add_category(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
            return
        ProductService.add_category(name)
        self.name_input.clear()
        self.load_categories()

    def handle_delete_selected(self):
        selected_items = self.table.selectionModel().selectedRows()

        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que querés eliminar {len(selected_items)} categorías?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ids = [self.table.item(row.row(), 0).text() for row in selected_items]
            for id in ids:
                ProductService.delete_category_by_id(int(id))
            self.load_categories()

    def rename_category_dialog(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        id = int(self.table.item(selected[0].row(), 0).text())
        old_name = self.table.item(selected[0].row(), 1).text()
        new_name, ok = QInputDialog.getText(self, "Renombrar categoría", "Nuevo nombre:", text=old_name)

        if ok:
            if not new_name:
                QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
                return
            new_name = new_name.strip()
            existing_names = [cat['name'] for cat in ProductService.get_all_categories()]
            if new_name in existing_names:
                QMessageBox.warning(self, "Error", "Ya existe una categoría con ese nombre.")
                return
            ProductService.rename_category(id, new_name)

            self.load_categories()

    def update_buttons_state(self):
        selected_count = len(self.table.selectionModel().selectedRows())
        if selected_count == 0:
            self.rename_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
        elif selected_count == 1:
            self.rename_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            self.rename_btn.setEnabled(False)
            self.delete_btn.setEnabled(True)

    def update_add_button_state(self):
        text = self.name_input.text().strip()
        self.add_btn.setEnabled(bool(text))

    def refresh(self):
        self.load_categories()