from db.db import get_connection
from datetime import datetime

from models.product import Product
from models.product_variant import ProductVariant
import models.category as Category


def save_transaction(product_id, quantity, type, obs='', variant_id=None,date = datetime.now().isoformat(timespec="seconds"), sale_id=None, purchase_id=None, conn=None):
    if type not in ["in", "out"]:
        raise ValueError("Tipo de movimiento debe ser 'in' o 'out'")

    if variant_id:
        # Mover stock de la variante
        if variant_id:
            variants = ProductVariant.get_by_product_id(product_id)
            variant = next((v for v in variants if v['id'] == variant_id), None)
            if not variant:
                raise ValueError(f"Variante con ID = {variant_id} no encontrada")
        else: variant = None

        if type == "in":
            variant['stock'] += quantity
            if not purchase_id:
                raise ValueError("Debe proporcionar un ID de compra para registrar una entrada")
            if sale_id is not None:
                sale_id = None
        else:
            if variant['stock'] < quantity:
                raise ValueError("Stock insuficiente en la variante")
            variant['stock'] -= quantity
            if not sale_id:
                raise ValueError("Debe proporcionar un ID de venta para registrar una salida")
            if purchase_id is not None:
                purchase_id = None
        ProductVariant.update(variant_id=variant["id"], variant_name=variant["variant_name"], stock=variant["stock"], price=variant["price"], stock_low=variant["stock_low"], conn=conn)
        Product.update_product(product_id=product_id, name=variant["name"], unit=variant["unit"], category_id=Category.get_id_by_name(variant["category"]), price=variant["price"], stock=variant["stock"], stock_low=variant["stock_low"], variants=None, conn=conn)
    else:

        # Actualizar stock del product
        products = Product.get_all()
        product = next((p for p in products if p.get("id") == product_id), None)
        if not product:
            raise ValueError(f"Producto con ID = {product_id} no encontrado")
        if type == "in":
            product["stock"] += quantity
            if purchase_id is None:
                raise ValueError("Debe proporcionar un ID de compra para registrar una entrada")
            if sale_id is not None:
                sale_id = None  # No se debe registrar una venta al hacer una entrada
        else:
            if product["stock"] < quantity:
                raise ValueError("Stock insuficiente para realizar el egreso")
            product["stock"] -= quantity
            if sale_id is None:
                raise ValueError("Debe proporcionar un ID de venta para registrar una salida")
            if purchase_id is not None:
                purchase_id = None

        Product.update_product(product_id=product["id"], name=product["name"], unit=product["unit"], category_id=Category.get_id_by_name(product["category"]), price=product["price"], stock=product["stock"], stock_low=product["stock_low"], variants=None, conn=conn)

    # registrar movimiento en la base de datos de movimientos
    if conn is None:
        conn = get_connection()
        conn.isolation_level = 'EXCLUSIVE'
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transaction_stock (product_id, variant_id, date, type, quantity, obs, sale_id, purchase_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_id, variant_id, date, type, quantity, obs, sale_id, purchase_id))


def get_transactions():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT ms.id, p.name, ms.date, ms.type, ms.quantity, ms.obs, ms.sale_id, ms.purchase_id
                    FROM transaction_stock ms
                    JOIN product p ON ms.product_id = p.id
                    ORDER BY ms.date DESC
                """)
        return cursor.fetchall()

