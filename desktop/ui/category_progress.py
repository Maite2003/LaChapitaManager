from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSizePolicy


class SalesCategoryProgress(QWidget):
    def __init__(self):
        super().__init__()
        self.sales = {}
        self.categories = []

        self.layout = QVBoxLayout(self)

        self.update_progress_bars()

    def set_data(self, sales, categories):
        """
        Set the sales and categories data for the progress bars.
        :param sales: Dictionary with category IDs as keys and dictionaries with 'name' and 'total' as values.
        :param categories: Dict mapping category IDs to category names.
        """
        self.sales = sales
        self.categories = categories
        self.update_progress_bars()

    def update_progress_bars(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total_sales = 0
        total_sales = sum(c['total'] for i,c in self.sales.items())
        if total_sales == 0:
            self.layout.addWidget(QLabel("No hay ventas para mostrar"))
            return

        # We create a progress bar for each category
        for cat_id, details in self.sales.items():
            cat_name = details.get('name', 'Desconocida')
            cat_total = details.get('total', 0)
            percent = int(cat_total / total_sales * 100)

            label = QLabel(f"{cat_name}: {percent}%")
            progress = QProgressBar()
            progress.setValue(percent)
            progress.setFormat(f"{percent}%")
            progress.setTextVisible(True)

            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            progress.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

            self.layout.addWidget(label)
            self.layout.addWidget(progress)
        self.layout.addStretch(1)  # Add stretch to push content to the top


