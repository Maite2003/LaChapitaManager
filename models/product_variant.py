from db.db import get_connection

class ProductVariant():
    def __init__(self, id, product_id, variant_name, stock=0, stock_low=0, price=0):
        self.id = id
        self.product_id = product_id
        self.variant_name = variant_name
        self.stock = stock
        self.stock_low = stock_low
        self.price = price

    def save(self, conn=None):
        """
        Save the product variant to the database.
        :param conn: Connection object, if None a new connection will be created.
        :return: ID of the saved variant.
        """
        if conn is None:
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'
        with conn:
            cursor = conn.cursor()
            if self.id:
                cursor.execute("""UPDATE product_variant SET variant_name=?, stock=?, price=?, stock_low=? WHERE id=?""",
                               (self.variant_name, self.stock, self.price, self.stock_low, self.id))
            else:
                cursor.execute("""INSERT INTO product_variant (product_id, variant_name, stock, stock_low, price) VALUES (?, ?, ?, ?, ?)""",
                               (self.product_id, self.variant_name, self.stock, self.stock_low, self.price))
                self.id = cursor.lastrowid
        return self.id

    @staticmethod
    def get_by_product_id(product_id):
        """Get all variants for a given product ID."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product_variant WHERE product_id=? GROUP BY variant_name", (product_id,))
            rows = cursor.fetchall()
            return [{'id': row[0], 'product_id': row[1], 'variant_name': row[2], 'stock': row[3], "stock_low": row[4], 'price': row[5]} for row in rows]

    @staticmethod
    def delete(variant_id, conn):
        """Delete a product variant by its ID."""
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM product_variant WHERE id=?", (variant_id,))

    @staticmethod
    def edit_stock(variant_id, quantity, type, conn=None):
        """ Edit stock of a product variant."""
        if type not in ["in", "out"]:
            raise ValueError("Tipo de movimiento debe ser 'in' o 'out'")

        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product_variant WHERE id=?", (variant_id,))
            x = cursor.fetchone()
            variant = {
                "id": x[0],
                "product_id": x[1],
                "variant_name": x[2],
                "stock": x[3],
                "stock_low": x[4],
                "price": x[5]
            }
            if not variant:
                raise ValueError("Variante no encontrada")

            if type == "out": # Stock decreases
                if quantity > variant["stock"]:
                    raise ValueError("No hay suficiente stock en la variante seleccionada")
                variant["stock"] -= quantity
            elif type == "in": # Stock increases
                variant["stock"] += quantity

            cursor.execute("""UPDATE product_variant SET stock=? WHERE id=?""", (variant["stock"], variant_id))