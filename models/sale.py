from models.product import Product
from models.stock import save_transaction, delete_transaction, update_transaction
from db.db import get_connection
from datetime import datetime

class Sale:
    def __init__(self, items, client_id, date=datetime.now().strftime('%Y-%m-%d'), id=None):
        self.id = id
        self.date = date
        """
        items = dictionary with (product_id, variant_id) as key and a dictionary with quantity and unit_price as value
        """
        self.items = items
        self.total = 0
        for key, value in items.items():
            self.total += value['quantity'] * value['unit_price']
        self.client_id = client_id


    def save(self):
        with get_connection() as conn:
            cursor = conn.cursor()

            if self.id:
                # Update sale
                cursor.execute("""
                    UPDATE sale
                    SET date = ?, client_id = ?, total = ?
                    WHERE id = ?
                """, (self.date, self.client_id, self.total, self.id))

            else:
                # New sale
                cursor.execute("""
                    INSERT INTO sale (date, client_id, total)
                    VALUES (?, ?, ?)
                """, (self.date, self.client_id, self.total))
                self.id = cursor.lastrowid
            self.save_details(conn=conn)
        return self.id

    def save_details(self, conn):
        with conn:
            cursor = conn.cursor()

            # Get old details
            cursor.execute("SELECT product_id, variant_id, quantity, unit_price from sale_detail WHERE sale_id = ?", (self.id,))
            old_products = {(row[0], row[1]):{'quantity':row[2], 'unit_price':row[3]} for row in cursor.fetchall()}
            delete = old_products.keys() - self.items.keys()

            # Delete products that are no longer in the sale
            for product_id, variant_id in delete:
                cursor.execute("DELETE FROM sale_detail WHERE sale_id = ? AND product_id = ? AND variant_id = ?", (self.id, product_id, variant_id))
                # Update the trsaction
                delete_transaction(product_id=product_id, variant_id=variant_id, type="out", quantity=old_products[(product_id, variant_id)]['quantity'], conn=conn, sale_id=self.id)

            for p, details in self.items.items():
                if p not in old_products: # New product
                    cursor.execute("INSERT INTO sale_detail (sale_id, product_id, variant_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)", (self.id, p[0], p[1], details["quantity"], details["unit_price"]))
                    # Actualizar stock del producto
                    save_transaction(product_id=p[0], variant_id=p[1], type="out", quantity=details["quantity"],conn=conn, sale_id=self.id)
                elif p in old_products: # Product was already on the sale
                    old = old_products.get(p, {}).get("quantity", 0)
                    print("old quantity was", old)
                    if details["quantity"] != old: # If the quantity has changed
                        # Update existing products
                        cursor.execute("UPDATE sale_detail SET variant_id = ?, quantity = ?, unit_price = ? WHERE sale_id = ? AND product_id = ?", (p[1], details["quantity"], details['unit_price'], self.id, p[0]))
                        update_transaction(product_id=p[0], variant_id=p[1], type="out", new_q=details["quantity"], conn=conn, sale_id=self.id)

    @staticmethod
    def get_by_id(sale_id):
        with get_connection() as conn:
            cur = conn.cursor()

            # Obtener datos generales de la venta
            cur.execute("""
                   SELECT sale.id, sale.date, sale.client_id, sale.total
                   FROM sale
                   WHERE sale.id = ?
               """, (sale_id,))
            general_info = cur.fetchone()


            # Obtener detalles de productos
            cur.execute("""
                   SELECT sd.product_id, sd.variant_id, sd.quantity, sd.unit_price, product.active
                   FROM sale_detail sd
                   JOIN product ON product.id = sd.product_id
                   WHERE sd.sale_id = ?
               """, (sale_id,))
            items = [(item[0], item[1], item[2], item[3], item[4]) for item in cur.fetchall()]

        return {
            "id": general_info[0],
            "date": datetime.strptime(general_info[1], "%Y-%m-%d").strftime("%d-%m-%Y"),
            "client_id": general_info[2] if general_info[2] else None,
            "total": general_info[3],
            "items": items  # List of (product_id, variant_id, quantity, unit_price)
        }

    @staticmethod
    def get_all(start_date, end_date):
        with get_connection() as conn:
            cursor = conn.cursor()
            if start_date is None or end_date is None:
                cursor.execute("""
                    SELECT sale.id, sale.date, sale.client_id, sale.total
                    FROM sale
                    ORDER BY sale.date DESC
                """)
            else:
                cursor.execute("""
                    SELECT sale.id, sale.date, sale.client_id, sale.total
                    FROM sale
                    WHERE sale.date BETWEEN ? AND ?
                    ORDER BY sale.date DESC
                """, (start_date, end_date))
            sales = cursor.fetchall()
        items = []
        for row in sales:
            sale = {
            "id": row[0],
            "date": datetime.strptime(row[1], "%Y-%m-%d").strftime("%d-%m-%Y"),
            "client_id": row[2] if row[2] else None,
            "total": row[3],
            }
            cursor.execute("""
                SELECT sd.product_id, sd.variant_id, sd.quantity, sd.unit_price, product.active
                FROM sale_detail sd
                JOIN product ON product.id = sd.product_id
                WHERE sd.sale_id = ?
                ORDER BY sd.product_id, sd.variant_id
            """, (sale["id"],))
            details = cursor.fetchall()
            sale_items = {}
            for item in details:
                key = (item[0], item[1])  # (product_id, variant_id)
                sale_items[key] = {"quantity": item[2], "unit_price": item[3], "active": item[4]}
            sale["items"] = sale_items
            items.append(sale)
        return items

    @staticmethod
    def delete(sale_id):
        with get_connection() as conn:
            cursor = conn.cursor()

            # Get items
            cursor.execute("SELECT product_id, variant_id, quantity FROM sale_detail WHERE sale_id = ?", (sale_id,))
            items = cursor.fetchall()
            for item in items:
                product_id, variant_id, quantity = item
                # Update stock of products
                Product.edit_stock(product_id=product_id, variant_id=variant_id, type="in", quantity=quantity, conn=conn)

            # Detele sale. The details and transaction erases automatically due to cascading
            cursor.execute("DELETE FROM sale WHERE id = ?", (sale_id,))

    @staticmethod
    def get_total(start_date, end_date):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(total) FROM sale
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
            result = cursor.fetchone()
            return result[0] if result[0] else 0

    @staticmethod
    def get_top5_products(start_date, end_date):
        with get_connection() as conn:
            cursor = conn.cursor()
            if start_date is None or end_date is None:
                cursor.execute("""
                    SELECT product.name, product_variant.variant_name, SUM(sd.quantity) as total_quantity
                    FROM sale_detail sd
                    JOIN sale ON sale.id = sd.sale_id
                    JOIN product ON product.id = sd.product_id
                    LEFT JOIN product_variant ON product_variant.id = sd.variant_id
                    WHERE product.active = 1
                    GROUP BY sd.product_id, sd.variant_id
                    ORDER BY total_quantity DESC
                    LIMIT 5
                """)
            else:
                cursor.execute("""
                    SELECT product.name, product_variant.variant_name, SUM(sd.quantity) as total_quantity
                    FROM sale_detail sd
                    JOIN sale s ON s.id = sd.sale_id
                    JOIN product ON product.id = sd.product_id
                    LEFT JOIN product_variant ON product_variant.id = sd.variant_id
                    WHERE s.date BETWEEN ? AND ?
                    AND product.active = 1
                    GROUP BY sd.product_id, sd.variant_id
                    ORDER BY total_quantity DESC
                    LIMIT 5
                """, (start_date, end_date))
            top_products = cursor.fetchall()

        return [(row[0], row[1], row[2]) for row in top_products] # product_name, variant_name, quantity

    @staticmethod
    def get_sales_by_categories(start_date, end_date):
        with get_connection() as conn:
            cursor = conn.cursor()

            if start_date is None or end_date is None:
                cursor.exceute("SELECT c.id AS category_id, c.name AS category_name, SUM(sd.quantity * sd.unit_price) AS total "
                       "FROM sale_detail sd "
                       "JOIN product p ON sd.product_id = p.id "
                       "JOIN category c ON p.category_id = c.id "
                       "GROUP BY c.name ORDER BY total DESC")
            else:
                cursor.execute("""
                    SELECT c.id AS category_id, c.name AS category_name, SUM(sd.quantity * sd.unit_price) AS total
                    FROM sale_detail sd
                    JOIN product p ON sd.product_id = p.id
                    JOIN category c ON p.category_id = c.id
                    JOIN sale s ON s.id = sd.sale_id
                    WHERE s.date BETWEEN ? AND ?
                    GROUP BY c.name ORDER BY total DESC, c.name
                """, (start_date, end_date))

            results = cursor.fetchall()
            categories = {}
            for row in results:
                category_id = row[0],
                category_name = row[1]
                total = row[2]
                categories[category_id] = ({
                    "name": category_name,
                    "total": total
                })

            print(categories)
            return categories
