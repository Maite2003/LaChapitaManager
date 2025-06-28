from models.product import Product
from models.stock import save_transaction, delete_transaction, update_transaction
from db.db import get_connection
from datetime import datetime

class Purchase:
    def __init__(self, items, supplier_id, date=datetime.now().strftime('%Y-%m-%d'), id=None):
        self.id = id
        self.date = date
        """
        items = dictionary with (product_id, variant_id) as key and a dictionary with quantity and unit_price as value
        """
        self.items = items
        self.total = 0
        for key, value in items.items():
            self.total += value['quantity'] * value['unit_price']
        self.supplier_id = supplier_id


    def save(self):
        with get_connection() as conn:
            cursor = conn.cursor()

            if self.id:
                # Update sale
                cursor.execute("""
                    UPDATE purchase
                    SET date = ?, supplier_id = ?, total = ?
                    WHERE id = ?
                """, (self.date, self.supplier_id, self.total, self.id))

            else:
                # New purchase
                cursor.execute("""
                    INSERT INTO purchase (date, supplier_id, total)
                    VALUES (?, ?, ?)
                """, (self.date, self.supplier_id, self.total))
                self.id = cursor.lastrowid
            self.save_details(conn=conn)
        return self.id

    def save_details(self, conn):
        with conn:
            cursor = conn.cursor()

            # Get old details
            cursor.execute("SELECT product_id, variant_id, quantity, unit_price from purchase_detail WHERE purchase_id = ?", (self.id,))
            old_products = {(row[0], row[1]):{'quantity':row[2], 'unit_price':row[3]} for row in cursor.fetchall()}
            delete = old_products.keys() - self.items.keys()

            # Delete products that are no longer in the purchase
            for product_id, variant_id in delete:
                cursor.execute("DELETE FROM purchase_detail WHERE purchase_id = ? AND product_id = ? AND variant_id = ?", (self.id, product_id, variant_id))
                # Update the trsaction
                delete_transaction(product_id=product_id, variant_id=variant_id, type="in", quantity=old_products[(product_id, variant_id)]['quantity'], conn=conn, purchase_id=self.id)

            for p, details in self.items.items():
                if p not in old_products: # New product
                    cursor.execute("INSERT INTO purchase_detail (purchase_id, product_id, variant_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)", (self.id, p[0], p[1], details["quantity"], details["unit_price"]))
                    # Actualizar stock del producto
                    save_transaction(product_id=p[0], variant_id=p[1], type="in", quantity=details["quantity"],conn=conn, purchase_id=self.id)
                elif p in old_products:
                    if details["quantity"] != old_products.get(p, {}).get("quantity", 0): # If the quantity has changed
                        # Update existing products
                        cursor.execute("UPDATE purchase_detail SET variant_id = ?, quantity = ?, unit_price = ? WHERE product_id = ?", (p[1], details["quantity"], details['unit_price'], self.id))
                        update_transaction(product_id=p[0], variant_id=p[1], type="in", new_q=details["quantity"], conn=conn, purchase_id=self.id)

    @staticmethod
    def get_by_id(purchase_id):
        with get_connection() as conn:
            cur = conn.cursor()

            # Obtener datos generales de la venta
            cur.execute("""
                   SELECT purchase.id, purchase.date, purchase.supplier_id, purchase.total
                   FROM purchase
                   WHERE purchase.id = ?
               """, (purchase_id,))
            general_info = cur.fetchone()


            # Obtener detalles de productos
            cur.execute("""
                   SELECT pd.product_id, pd.variant_id, pd.quantity, pd.unit_price, product.active
                   FROM purchase_detail pd
                   JOIN product ON product.id = pd.product_id
                   WHERE pd.purchase_id = ?
                   ORDER BY pd.product_id, pd.variant_id
               """, (purchase_id,))
            items = [(item[0], item[1], item[2], item[3], item[4]) for item in cur.fetchall()]

        return {
            "id": general_info[0],
            "date": datetime.strptime(general_info[1], "%Y-%m-%d").strftime("%d-%m-%Y"),
            "supplier_id": general_info[2] if general_info[2] else None,
            "total": general_info[3],
            "items": items  # List of (product_id, variant_id, quantity, unit_price)
        }

    @staticmethod
    def get_all(start_date, end_date):
        with get_connection() as conn:
            cursor = conn.cursor()
            if start_date is None or end_date is None:
                cursor.execute("""
                    SELECT purchase.id, purchase.date, purchase.supplier_id, purchase.total
                    FROM purchase
                    ORDER BY purchase.date DESC
                """)
            else:
                cursor.execute("""
                    SELECT purchase.id, purchase.date, purchase.supplier_id, purchase.total
                    FROM purchase
                    WHERE purchase.date BETWEEN ? AND ?
                    ORDER BY purchase.date DESC
                """, (start_date, end_date))
            purchases = cursor.fetchall()
        items = []
        for row in purchases:
            purchase = {
            "id": row[0],
            "date": datetime.strptime(row[1], "%Y-%m-%d").strftime("%d-%m-%Y"),
            "supplier_id": row[2] if row[2] else None,
            "total": row[3],
            }
            cursor.execute("""
                SELECT pd.product_id, pd.variant_id, pd.quantity, pd.unit_price, product.active
                FROM purchase_detail pd
                JOIN product ON product.id = pd.product_id
                WHERE pd.purchase_id = ?
                ORDER BY pd.product_id, pd.variant_id
            """, (purchase["id"],))
            details = cursor.fetchall()
            purchase_items = {}
            for item in details:
                key = (item[0], item[1])  # (product_id, variant_id)
                purchase_items[key] = {"quantity": item[2], "unit_price": item[3], "active": item[4]}
            purchase["items"] = purchase_items
            items.append(purchase)
        return items

    @staticmethod
    def delete(purchase_id):
        with get_connection() as conn:
            cursor = conn.cursor()

            # Get items
            cursor.execute("SELECT product_id, variant_id, quantity FROM purchase_detail WHERE purchase_id = ?", (purchase_id,))
            items = cursor.fetchall()
            for item in items:
                product_id, variant_id, quantity = item
                # Update stock of products
                Product.edit_stock(product_id=product_id, variant_id=variant_id, type="out", quantity=quantity, conn=conn)

            # Detele purchase. The details and transaction erases automatically due to cascading
            cursor.execute("DELETE FROM purchase WHERE id = ?", (purchase_id,))

    @staticmethod
    def get_total(start_date, end_date):
        """
        Get the total purchase amount within a specified date range.
        If no dates are provided, it returns the total purchase amount without filtering.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(total) FROM purchase
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
            total = cursor.fetchone()[0]
            return total if total else 0