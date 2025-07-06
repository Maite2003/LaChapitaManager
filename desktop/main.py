import os
import sys

from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from desktop.ui.main_window import MainWindow
from db.db import initialize_db
from utils import config
from utils.path_utils import get_writable_path, resource_path

if __name__ == "__main__":

    initialize_db()

    settings_path = os.path.join(get_writable_path(), "lachapita_config.ini")
    settings = QSettings(settings_path, QSettings.Format.IniFormat)
    config.backup_drive = settings.value("backup_drive_enabled", False, type=bool)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/icon.png")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())