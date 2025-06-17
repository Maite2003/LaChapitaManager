from db.db import get_connection

class ProductVariant():
    def __init__(self, product_id, variant_name, stock=0, stock_low=0, price=None, id=None):
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
                cursor.execute("""INSERT INTO product_variant (product_id, variant_name, stock, price) VALUES (?, ?, ?, ?)""",
                               (self.product_id, self.variant_name, self.stock, self.price))
                self.id = cursor.lastrowid

    @staticmethod
    def update(variant_id, variant_name, stock, price, stock_low, conn=None):
        if conn is None:
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'
        with conn:
            cursor = conn.cursor()
            cursor.execute("""UPDATE product_variant SET variant_name=?, stock=?, price=?, stock_low=? WHERE id=?""",
                               (variant_name, stock, price, stock_low, variant_id))

    @staticmethod
    def get_by_product_id(product_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product_variant WHERE product_id=?", (product_id,))
            rows = cursor.fetchall()
            return [{'id': row['id'], 'product_id': row['product_id'], 'variant_name': row['variant_name'], 'stock': row['stock'], "stock_low": row["stock_low"], 'price': row['price']} for row in rows]

    @staticmethod
    def delete(variant_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM product_variant WHERE id=?", (variant_id,))
