import sqlite3
import os
from utils.path_utils import resource_path
import shutil
from utils.path_utils import get_writable_path

# Get the writable database path based on the operating system. For the executable, it will be in the AppData folder on Windows.
def get_writable_db_path():
    app_folder = get_writable_path()
    return os.path.join(app_folder, 'lachapita.db')

# Prepare the database by copying the bundled database to a writable location if it doesn't exist.
def prepare_database():
    writable_db = get_writable_db_path()
    # If the database does not exist in the writable location, copy it from the bundled resources.
    if not os.path.exists(writable_db):
        bundled_db = resource_path("data/lachapita.db")
        shutil.copyfile(bundled_db, writable_db)
    return writable_db

def get_connection():
    db_path = prepare_database()
    return sqlite3.connect(db_path)

def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        schema_path = resource_path("db/schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = f.read()
            cursor.executescript(schema)


