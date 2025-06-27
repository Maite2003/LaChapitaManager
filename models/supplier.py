from db.db import get_connection

class Supplier:
    def __init__(self, name, surname, phone=None, mail=None, id=None):
        self.id = id
        self.name = name
        self.surname = surname
        self.phone = phone
        self.mail = mail

    def save(self):
        with get_connection() as conn:
            cur = conn.cursor()
            if self.id:
                cur.execute("""
                    UPDATE supplier
                    SET name=?, surname=?, phone=?, mail=?
                    WHERE id=?
                """, (self.name, self.surname, self.phone, self.mail, self.id))
            else:
                cur.execute("""
                    INSERT INTO supplier (name, supplier, phone, mail)
                    VALUES (?, ?, ?, ?)
                """, (self.name, self.surname, self.phone, self.mail))
                self.id = cur.lastrowid

    @staticmethod
    def get_all():
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM supplier")
            filas = cur.fetchall()
            return [Supplier(*fila[1:], id=fila[0]) for fila in filas]

    @staticmethod
    def delete(supplier_id):
        with get_connection() as conn:
            conn.execute("DELETE FROM supplier WHERE id=?", (supplier_id,))

    @staticmethod
    def get_by_id(supplier_id):
        if not supplier_id or supplier_id < 0:
            return None
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM supplier WHERE id=?", (supplier_id,))
            fila = cur.fetchone()
            if fila:
                return Supplier(*fila[1:], id=fila[0])
            return None