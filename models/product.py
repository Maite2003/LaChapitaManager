from db.db import get_connection
from models.product_variant import ProductVariant
import models.category as Category

class Product():
    def __init__(self, name, category, unit, price, stock=0, stock_low=0, id = None):
        self.id = id
        self.name = name
        self.category = category
        self.unit = unit
        self.price = price
        self.stock = stock
        self.stock_low = stock_low

    # Metodo que actualiza el producto en la data base con sus atributos
    # Si no existe el producto en la database (no hay id coincidente), crea una nueva entrada
    def save(self, conn=None):
        if conn is None:
            # Si no se pasa una conexión, se obtiene una nueva
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'
        with conn:  # Usar el contexto para manejar la conexión
            cursor = conn.cursor()
            if self.id:  # Enable WAL mode
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
        return self.id  # Devuelve el id del producto recién creado o actualizado



    # Devuelve una lista de todos los productos en la base de datos
    @staticmethod
    def get_all():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                   SELECT product.id, product.name, category.name AS category, product.unit, product.price, product.stock, product.stock_low
                   FROM product JOIN category ON product.category_id = category.id
               """)
            # Devuelve todas las filas resultantes de haber ejecutado la query de execute
            products = [dict(row) for row in cursor.fetchall()]

            # Obtener todas las variantes agrupadas por producto_id
            cursor.execute("""
                    SELECT id, product_id, variant_name, stock, stock_low, price
                    FROM product_variant
                """)
            variants_by_product = {}
            for row in cursor.fetchall():
                variant = dict(row)
                product_id = variant["product_id"]
                variants_by_product.setdefault(product_id, []).append({
                    "id": variant["id"],
                    "name": variant["variant_name"],
                    "stock": variant["stock"],
                    "stock_low": variant["stock_low"],
                    "price": variant["price"],
                })

            # Agregar las variantes a cada producto
            # Agregar la lista de variantes a cada producto
            for product in products:
                product_id = product["id"]
                product["variants"] = variants_by_product.get(product_id, [])

            # Devuelve una lista con un producto por fila de filas
        return products

    # Elimina un producto de la data base por su id
    @staticmethod
    def delete(product_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM product WHERE id=?", (product_id,))

    @classmethod
    def exists_name(cls, name):
        """
        Verifica si ya existe un producto con el mismo título.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM product WHERE name=?", (name,))
            count = cursor.fetchone()[0]
            return count > 0


    @staticmethod
    def get_by_id(product_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT product.id, product.name, product.unit, product.price, product.stock, product.stock_low, category.name AS category FROM product JOIN category ON product.category_id = category.id WHERE product.id=?", (product_id,))
            fila = cursor.fetchone()
            if fila:
                return {'id': fila['id'], 'name': fila["name"], 'category': fila['category'], 'unit': fila['unit'], 'price': fila['price'], 'stock': fila['stock'], 'stock_low': fila['stock_low']}
            return None

    @staticmethod
    def update_product(product_id, name, unit, category_id, price, stock, stock_low, variants=None, conn=None):
        if conn is None:
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'
        with conn:
            cursor = conn.cursor()
            cursor.execute("""UPDATE product SET name=?, unit=?, category_id=?, price=?, stock=?, stock_low=? WHERE id=?""",
                           (name, unit, category_id, price, stock, stock_low, product_id))
            if variants is not None:
                Product.save_variants(variants_list=variants, id=product_id, conn=conn)

    @staticmethod
    def get_product_with_variants(p):
        if p:
            variants = ProductVariant.get_by_product_id(p["id"])
            p['variants'] = variants
        return p

    @staticmethod
    def save_variants(variants_list, id, conn=None):
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

            # Obtener variantes actuales del producto
            cursor.execute("SELECT id FROM product_variant WHERE product_id=?", (id,))
            # Obtener los ids de las variantes actuales
            current_variants = {row[0] for row in cursor.fetchall()}

            # Variantes que vienen con id (para actualizar)
            incoming_ids = {v['id'] for v in variants_list if 'id' in v and v['id'] is not None}

            # Variantes a eliminar (las que están en DB pero no vienen en la lista)
            to_delete = current_variants - incoming_ids
            for vid in to_delete:
                cursor.execute("DELETE FROM product_variant WHERE id=?", (vid,))

            # Actualizar o insertar variantes
            for variant in variants_list:
                if 'id' in variant and variant['id'] in current_variants:
                    # Actualizar
                    cursor.execute("""
                        UPDATE product_variant SET variant_name=?, stock=?, stock_low=?, price=? WHERE id=?
                    """, (variant['variant_name'], variant.get('stock', 0), variant.get('stock_low',0), variant.get('price'), variant['id']))
                else:
                    # Insertar nuevo
                    cursor.execute("""
                        INSERT INTO product_variant (product_id, variant_name, stock, stock_low, price) VALUES (?, ?, ?, ?, ?)
                    """, (id, variant['variant_name'], variant.get('stock', 0), variant.get('stock_low', 0), variant.get('price')))

    @staticmethod
    def count_by_category(name):
        with get_connection() as conn:
            cursor = conn.cursor()
            categories = Category.get_all()
            names = [name['name'] for name in categories]
            if name not in names:
                return 0
            cursor.execute("SELECT COUNT(*) FROM product WHERE category_id = ?", (Category.get_id_by_name(name),))
            result = cursor.fetchone()

            return result[0] if result else 0