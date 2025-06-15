from db.db import get_connection

def get_all_categories():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
    return [dict(row) for row in cursor.fetchall()]

def add_category(nombre):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre,))

