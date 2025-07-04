from db.db import get_connection

class Client:
    def __init__(self, name, surname="", phone="", mail="", id=None):
        self.id = id
        self.name = name
        self.surname = surname
        self.mail = mail
        self.phone = phone

    def save(self):
        """
        Saves the client to the database. If the client has an ID, it updates the existing record; otherwise, it creates a new one.
        :return: ID of the saved client.
        """
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
        return self.id

    @staticmethod
    def get_all():
        """
        Retrieves all clients from the database, ordered by name and surname.
        :return: List of dictionaries containing client information.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM client ORDER BY name, surname")
            filas = cur.fetchall()
            return [{"name": fila[1], "surname": fila[2], "phone": fila[3], "mail": fila[4], "id": fila[0]} for fila in filas]

    @staticmethod
    def delete(client_id):
        """Deletes a client from the database by ID."""
        with get_connection() as conn:
            conn.execute("DELETE FROM client WHERE id=?", (client_id,))

    @staticmethod
    def get_by_id(client_id):
        """Retrieves a client from the database by ID."""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM client WHERE id=?", (client_id,))
            fila = cur.fetchone()
            if fila:
                return {"name": fila[1], "surname": fila[2], "phone": fila[3], "mail": fila[4], "id": fila[0]}
            return None
