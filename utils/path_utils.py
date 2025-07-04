import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_writable_path():
    appdata = os.getenv('APPDATA')
    app_folder = os.path.join(appdata, 'LaChapitaManager')
    os.makedirs(app_folder, exist_ok=True)
    return app_folder

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller .exe"""
    if getattr(sys, 'frozen', False):  # If running as bundled .exe
        base_path = sys._MEIPASS
    else:  # If running in a normal Python environment
        base_path = BASE_DIR
    return os.path.join(base_path, relative_path)
