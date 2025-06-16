import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from db.db import initialize_db

if __name__ == "__main__":

    initialize_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())