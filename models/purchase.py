from stock import save_transaction
from db.db import get_connection
from datetime import datetime

def save_purchase(items, supplier, date=datetime.now().isoformat(timespec="seconds")):
    """
    items = lista de tuplas (producto_id, cantidad, precio_unitario)
    """

    total = sum(q * price for _, quantity, price in items)

    with get_connection() as conn:
        cursor = conn.cursor()

        # Registrar la compra
        cursor.execute("""
            INSERT INTO purchase (date, total, supplier_id)
            VALUES (?, ?, ?)
        """, (date, total, supplier))

        purchase_id = cursor.lastrowid

        # Registrar cada item de la compra
        for product_id, quantity, unit_price in items:
            cursor.execute("""
                INSERT INTO purchase_detail (purchase_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (purchase_id, product_id, quantity, unit_price))

            # Actualizar stock del producto
            save_transaction(product_id=product_id, type="out", quantity=quantity, purchase_id=purchase_id, conn=conn)
    return purchase_id