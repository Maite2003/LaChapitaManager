from db.db import get_connection

class Supplier:
    def __init__(self, name, surname, phone=None, mail=None, id=None):
        self.id = id
        self.name = name
        self.surname = surname
        self.phone = phone
        self.mail = mail

    def save(self):
        """
        Save the supplier to the database. If the supplier has an id, it updates the existing record.
        If the supplier does not have an id, it creates a new record.
        :return: The id of the supplier.
        """
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
                    INSERT INTO supplier (name, surname, phone, mail)
                    VALUES (?, ?, ?, ?)
                """, (self.name, self.surname, self.phone, self.mail))
                self.id = cur.lastrowid
        return self.id

    @staticmethod
    def get_all():
        """
        Get all suppliers from the database.
        :return: A list dictionaries with supplier details.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM supplier")
            filas = cur.fetchall()
            return [{'id': fila[0], 'name':fila[1], 'surname':fila[2], 'phone':fila[3], 'mail':fila[4]} for fila in filas]

    @staticmethod
    def delete(supplier_id):
        """
        Delete a supplier from the database by its id.
        """
        with get_connection() as conn:
            conn.execute("DELETE FROM supplier WHERE id=?", (supplier_id,))

    @staticmethod
    def get_by_id(supplier_id):
        """
        Get a supplier by its id.
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM supplier WHERE id=?", (supplier_id,))
            fila = cur.fetchone()
            if fila:
                return {'id': fila[0], 'name': fila[1], 'surname': fila[2], 'phone': fila[3], 'mail': fila[4]}
            return None