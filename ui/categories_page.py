from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit, QListWidget, \
    QListWidgetItem, QMessageBox, QInputDialog, QTableWidget, QTableWidgetItem, QHeaderView
import models.category as Category
from models.product import Product


class CategoriesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.layout().addWidget(QLabel("Categorías"))

        # Lista de categorías
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Categoría", "Cantidad de productos"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.update_buttons_state)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.layout().addWidget(self.table)

        # Formulario para agregar nueva categoría
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nueva categoría")
        self.name_input.textChanged.connect(self.update_add_button_state)

        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self.handle_add_category)
        self.update_add_button_state()

        # Boton para eliminar categorias seleccionadas
        self.delete_btn = QPushButton("Eliminar")
        self.delete_btn.setEnabled(False)  # Inicialmente deshabilitado
        self.delete_btn.clicked.connect(self.handle_delete_selected)

        # Boton para renombrar categoria seleccionada
        self.rename_btn = QPushButton("Renombrar")
        self.rename_btn.setEnabled(False)  # Inicialmente deshabilitado
        self.rename_btn.clicked.connect(self.rename_category_dialog)

        form_layout.addWidget(self.delete_btn)
        form_layout.addWidget(self.rename_btn)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.add_btn)

        self.layout().addLayout(form_layout)

        self.load_categories()

    def load_categories(self):
        self.table.setRowCount(0)
        categories = Category.get_all()  # Cada categoría debería tener al menos 'name'

        for row, cat in enumerate(categories):
            name = cat['name']
            count = Product.count_by_category(name=name)

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(str(count)))

    def handle_add_category(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
            return
        try:
            Category.add_category(name)
        except Exception as e:
            print("Excepción capturada:", e)
        else:
            self.name_input.clear()
            self.load_categories()

    def handle_delete_selected(self):
        selected_items = self.table.selectionModel().selectedRows()
        if not selected_items:
            QMessageBox.warning(self, "Error", "No se seleccionó ninguna categoría.")
            return

        nombres = [self.table.item(row.row(), 0).text() for row in selected_rows]

        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que querés eliminar las siguientes categorías?\n\n{', '.join(nombres)}\n\nEsto también eliminará los productos asociados.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                for nombre in nombres:
                    Category.delete_by_name(nombre)  # implementalo en category.py
                    self.load_categories()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudieron eliminar:\n{str(e)}")

    def rename_category_dialog(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        old_name = self.table.item(selected[0].row(), 0).text()
        new_name, ok = QInputDialog.getText(self, "Renombrar categoría", "Nuevo nombre:", text=old_name)

        if ok:
            new_name = new_name.strip()
            if not new_name:
                QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
                return

            existing_names = [cat['name'] for cat in Category.get_all()]
            if new_name in existing_names:
                QMessageBox.warning(self, "Error", "Ya existe una categoría con ese nombre.")
                return
            try:
                Category.rename_category(old_name, new_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo renombrar:\n{str(e)}")

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