from db.db import get_connection

class Client:
    def __init__(self, name, surname="", phone="", mail="", id=None):
        self.id = id
        self.name = name
        self.surname = surname
        self.mail = mail
        self.phone = phone

    def save(self):
        with get_connection() as conn:
            cur = conn.cursor()
            if self.id:
                cur.execute("""
                    UPDATE client
                    SET name=?, surname=?, phone=?, mail=?
                    WHERE id=?
                """, (self.name, self.surname, self.phone, self.mail, self.id))
            else:
                cur.execute("""
                    INSERT INTO client (name, surname, phone, mail)
                    VALUES (?, ?, ?, ?)
                """, (self.name, self.surname, self.phone, self.mail))
                self.id = cur.lastrowid

    @staticmethod
    def get_all():
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM client ORDER BY name, surname")
            filas = cur.fetchall()
            return [{"name": fila["name"], "surname": fila["surname"], "phone": fila["phone"], "mail": fila["mail"], "id": fila["id"]} for fila in filas]

    @staticmethod
    def delete(client_id):
        with get_connection() as conn:
            conn.execute("DELETE FROM client WHERE id=?", (client_id,))

    @staticmethod
    def get_by_id(client_id):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM client WHERE id=?", (client_id,))
            fila = cur.fetchone()
            if fila:
                return Client(name=fila["name"], surname=fila["surname"], phone=fila["phone"], mail=fila["mail"], id=fila["id"])
            return None
