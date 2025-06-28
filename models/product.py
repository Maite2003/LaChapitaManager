from collections import defaultdict

from db.db import get_connection
from models.product_variant import ProductVariant
from models.category import Category

class Product():
    def __init__(self, name, category, unit, price, stock=0, stock_low=0, id = None, variants=None):
        self.id = id
        self.name = name
        self.category = category
        self.unit = unit
        self.price = price
        self.stock = stock
        self.stock_low = stock_low
        self.variants = variants if variants is not None else []

    # Metodo que actualiza el producto en la data base con sus atributos
    # Si no existe el producto en la database (no hay id coincidente), crea una nueva entrada
    def save(self, conn=None):
        if conn is None:
            # Si no se pasa una conexión, se obtiene una nueva
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'
        with conn:  # Usar el contexto para manejar la conexión
            cursor = conn.cursor()
            if self.id:
                cursor.execute("""UPDATE product SET name=?, category_id=?, unit=?, price=?, 
                                    stock=?, stock_low=? WHERE id=?
                                """, (self.name, self.category, self.unit, self.price,
                                      self.stock, self.stock_low, self.id))
            else:
                cursor.execute("""INSERT INTO product (name, category_id, unit, price, 
                                    stock, stock_low)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (self.name, self.category, self.unit, self.price,
                                      self.stock, self.stock_low))
                self.id = cursor.lastrowid

            if self.variants is not []:
                # Guardar variantes junto con el producto
                self.save_variants(variants_list=self.variants, conn=conn)

        return self.id  # Devuelve el id del producto recién creado o actualizado

    def save_variants(self, variants_list, conn=None):
        """
        Updates, deletes or creates variants depending on the contents of variant_list
        - If the element in variants_list contains id, then updates existing variant with that id
        - If the element in variants_list does not contain id, then creates a new variant
        - If the variant exists in the database but not in variants_list, it is deleted
        """
        if conn is None:
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'

        with conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM product_variant WHERE product_id=?", (self.id,))
            current_variant_ids = {row[0] for row in cursor.fetchall()}

            incoming_ids = []
            for v in variants_list:
                vid = v.get("id", None)
                if vid is not None:
                    incoming_ids.append(vid)

            # Delete removed variants
            to_delete = current_variant_ids - set(incoming_ids)
            for vid in to_delete:
                ProductVariant.delete(vid, conn)

            # Insert or update variants
            for v in variants_list:
                ProductVariant(id= v["id"], product_id=self.id, variant_name=v["variant_name"], stock=v['stock'], stock_low=v['stock_low'], price=v['price']).save(conn)

    # Devuelve una lista de todos los productos en la base de datos
    @staticmethod
    def get_all(active=2):
        with get_connection() as conn:
            cursor = conn.cursor()
            if active == 2:
                cursor.execute("""
                       SELECT product.id, product.name, category.name AS category, product.unit, product.price, product.stock, product.stock_low
                       FROM product JOIN category ON product.category_id = category.id
                       GROUP BY product.name, category.name
                   """)
            elif active == 1:
                cursor.execute("""
                       SELECT product.id, product.name, category.name AS category, product.unit, product.price, product.stock, product.stock_low
                       FROM product JOIN category ON product.category_id = category.id WHERE product.active=1 
                       GROUP BY product.name, category.name
                   """)
            else:
                cursor.execute("""
                       SELECT product.id, product.name, category.name AS category, product.unit, product.price, product.stock, product.stock_low
                       FROM product JOIN category ON product.category_id = category.id WHERE product.active=0
                       GROUP BY product.name, category.name
                   """)
            # Devuelve todas las filas resultantes de haber ejecutado la query de execute
            products = [dict(row) for row in cursor.fetchall()]

            for product in products:
                product_id = product["id"]
                product["variants"] = ProductVariant.get_by_product_id(product_id)

        return products

    @staticmethod
    def get_by_id(product_id, conn=None):
        if not conn:
            conn = get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT product.id, product.name, product.unit, product.price, product.stock, product.stock_low, product.category_id FROM product WHERE product.id=?",
                (product_id,))
            fila = cursor.fetchone()
            if fila:
                variants = ProductVariant.get_by_product_id(fila["id"])
                return {'id': fila['id'], 'name': fila["name"], 'category': fila['category_id'], 'unit': fila['unit'],
                        'price': fila['price'], 'stock': fila['stock'], 'stock_low': fila['stock_low'], "variants": variants}
            return None

    # Elimina un producto de la data base por su id
    @staticmethod
    def delete(product_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE product SET active=0 WHERE id=?", (product_id,))

    @staticmethod
    def exists_name(name):
        """
        Verifica si ya existe un producto con el mismo título.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM product WHERE name=?", (name,))
            count = cursor.fetchone()[0]
            return count > 0

    @staticmethod
    def count_by_category(name):
        with get_connection() as conn:
            cursor = conn.cursor()
            categories = Category.get_all()
            names = [name['name'] for name in categories]
            if name not in names:
                return 0
            cursor.execute("SELECT COUNT(*) FROM product WHERE category_id = ? AND active = ?", (Category.get_id_by_name(name), 1,))
            result = cursor.fetchone()

            return result[0] if result else 0

    @staticmethod
    def edit_stock(product_id, variant_id, quantity, type, conn=None):
        """
        Edita el stock de un producto o variante.
        Si se proporciona variant_id, edita el stock de la variante.
        Si no se proporciona variant_id, edita el stock del producto.
        """

        with conn:
            cursor = conn.cursor()
            if variant_id:
                ProductVariant.edit_stock(variant_id=variant_id, quantity=quantity, type=type, conn=conn)

                # Calculates the stock of the product as the sum of the variant's stock
                cursor.execute("SELECT stock FROM product_variant WHERE product_id=?", (product_id,))
                q = cursor.fetchall()
                new_stock = 0
                for row in q:
                    new_stock += row[0]
            else:
                cursor.execute("SELECT stock FROM product WHERE id=?", (product_id,))
                stock = cursor.fetchone()[0]
                if type == "out":
                    new_stock = stock - quantity
                elif type == "in":
                    new_stock = stock + quantity
                cursor.execute("UPDATE product SET stock=? WHERE id=?", (new_stock, product_id))


            cursor.execute("UPDATE product SET stock=? WHERE id=?", (new_stock, product_id))

    @staticmethod
    def check_stock(actual_products):
        with get_connection() as conn:
            cursor = conn.cursor()
            for (product_id, variant_id), details in actual_products.items():
                if variant_id is not None:
                    cursor.execute("SELECT stock FROM product_variant WHERE id = ?", (variant_id,))
                    stock = cursor.fetchone()
                    if not stock or stock[0] < details['quantity']:
                        return False, (product_id, variant_id, details['quantity'], stock[0] if stock else None)
                else:
                    cursor.execute("SELECT stock FROM product WHERE id = ?", (product_id,))
                    stock = cursor.fetchone()
                    if not stock or stock[0] < details['quantity']:
                        return False, (product_id, None, details['quantity'], stock[0] if stock else None)
        return True, None

    @staticmethod
    def get_low_stock(q):
        with get_connection() as conn:
            cursor = conn.cursor()

            # Get all low-stock variants (where variant stock is below threshold)
            cursor.execute("""
                    SELECT 
                        p.name AS product_name,
                        pv.variant_name,
                        pv.stock,
                        pv.stock_low
                    FROM product_variant pv
                    JOIN product p ON p.id = pv.product_id
                    WHERE pv.stock <= pv.stock_low
                    ORDER BY pv.stock ASC
                """)
            low_stock_variants = cursor.fetchall()

            # Now, get all products with no variants and low stock
            cursor.execute("""
                    SELECT 
                        p.name AS product_name,
                        NULL AS variant_name,
                        p.stock,
                        p.stock_low
                    FROM product p
                    WHERE p.stock <= p.stock_low
                    AND p.active = 1
                      AND p.id NOT IN (SELECT DISTINCT product_id FROM product_variant)
                    ORDER BY p.stock ASC
                """)
            low_stock_products = cursor.fetchall()

            # Merge and take the first `limit` items overall
            all_low_stock = low_stock_variants + low_stock_products

            all_low_stock = [dict(zip(["product_name", "variant_name", "stock", "low_stock"], row)) for row in all_low_stock]

            if q: return all_low_stock[:q]
            else: return all_low_stock
