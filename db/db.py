import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__),"..", "data", "lachapita.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__),"schema.sql")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)  # espera hasta 10 segundos si está bloqueada
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = f.read()
            cursor.executescript(schema)


