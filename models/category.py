from db.db import get_connection

class Category:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    @staticmethod
    def get_all():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM category ORDER BY name")
            all = cursor.fetchall()
        return [{'id': row['id'], 'name': row['name']} for row in all]

    def add_category(name):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO category (name) VALUES (?)", (name,))

    @staticmethod
    def delete_by_id(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM category WHERE id = ?", (id,))
            if cursor.rowcount == 0:
                raise ValueError(f"No se encontró la categoría con id: {id}")
            conn.commit()

    @staticmethod
    def rename_category(id, new_name):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE category SET name = ? WHERE id = ?", (new_name, id))

    @staticmethod
    def get_id_by_name(name):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM category WHERE name = ?", (name,))
            row = cursor.fetchone()
            return row[0] if row else None
