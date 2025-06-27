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
        if conn is None:
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'
        with conn:
            cursor = conn.cursor()
            if self.id:
                cursor.execute("""UPDATE product_variant SET variant_name=?, stock=?, price=? WHERE id=?""",
                               (self.variant_name, self.stock, self.price, self.id))
            else:
                cursor.execute("""INSERT INTO product_variant (product_id, variant_name, stock, stock_low, price) VALUES (?, ?, ?, ?, ?)""",
                               (self.product_id, self.variant_name, self.stock, self.stock_low, self.price))
                self.id = cursor.lastrowid

    @staticmethod
    def get_by_product_id(product_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product_variant WHERE product_id=? GROUP BY variant_name", (product_id,))
            rows = cursor.fetchall()
            return [{'id': row['id'], 'product_id': row['product_id'], 'variant_name': row['variant_name'], 'stock': row['stock'], "stock_low": row["stock_low"], 'price': row['price']} for row in rows]

    @staticmethod
    def delete(variant_id, conn):
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM product_variant WHERE id=?", (variant_id,))

    @staticmethod
    def edit_stock(variant_id, quantity, type, conn=None):
        if type not in ["in", "out"]:
            raise ValueError("Tipo de movimiento debe ser 'in' o 'out'")

        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product_variant WHERE id=?", (variant_id,))
            x = cursor.fetchone()
            variant = dict(zip([col[0] for col in cursor.description], x)) if x else None
            if not variant:
                raise ValueError("Variante no encontrada")

            if type == "out":
                if quantity > variant["stock"]:
                    raise ValueError("No hay suficiente stock en la variante seleccionada")
                variant["stock"] -= quantity
            elif type == "in":
                variant["stock"] += quantity


            cursor.execute("""UPDATE product_variant SET stock=? WHERE id=?""", (variant["stock"], variant_id))