import sqlite3
import os
from utils.path_utils import resource_path
from utils.path_utils import get_writable_path

# Get the writable database path based on the operating system. For the executable, it will be in the AppData folder on Windows.
def get_writable_db_path():
    app_folder = get_writable_path()
    return os.path.join(app_folder, 'lachapita.db')

def get_connection():
    writable_db = get_writable_db_path()
    return sqlite3.connect(writable_db)

def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        schema_path = resource_path("db/schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = f.read()
            cursor.executescript(schema)


