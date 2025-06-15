from db.db import get_connection
from datetime import datetime

from product import Product

def save_transaction(product_id, quantity, type, obs ="", date = datetime.now().isoformat(timespec="seconds"), sale_id=None, purchase_id=None, conn=None):
    if type not in ["entrada", "salida"]:
        raise ValueError("Tipo de movimiento debe ser 'entrada' o 'salida'")

    # Actualizar stock del product
    products = Product.get_all()
    product = next((p for p in products if p.id == product_id), None)

    if not product:
        raise ValueError(f"Producto con ID = {product_id} no encontrado")

    if type == "in":
        product.stock += quantity
        if purchase_id is None:
            raise ValueError("Debe proporcionar un ID de compra para registrar una entrada")
        if sale_id is not None:
            sale_id = None  # No se debe registrar una venta al hacer una entrada
    else:
        if product.stock < quantity:
            raise ValueError("Stock insuficiente para realizar el egreso")
        product.stock -= quantity
        if sale_id is None:
            raise ValueError("Debe proporcionar un ID de venta para registrar una salida")
        if purchase_id is not None:
            purchase_id = None

    product.save(conn)

    # registrar movimiento en la base de datos de movimientos
    if conn is None:
        conn = get_connection()
        conn.isolation_level = 'EXCLUSIVE'
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transaction_stock (product_id, date, type, quantity, obs, sale_id, purchase_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_id, date, type, quantity, obs, sale_id, purchase_id))


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


