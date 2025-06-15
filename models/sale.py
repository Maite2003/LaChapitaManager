from stock import save_transaction
from db.db import get_connection
from datetime import datetime

def save_sale(items, client, date = datetime.now().isoformat(timespec="seconds")):
    """
    items = lista de tuplas (product_id, quantity, unit_price)
    """
    total = sum(quantity * price for _, quantity, price in items)

    with get_connection() as conn:
        cursor = conn.cursor()

        # Registrar la venta
        cursor.execute("""
            INSERT INTO sale (date, client_id, total)
            VALUES (?, ?, ?)
        """, (date, client, total))

        sale_id = cursor.lastrowid

        # Registrar cada item de la venta
        for product_id, quantity, unit_price in items:
            cursor.execute("""
                INSERT INTO sale_detail (sale_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (sale_id, product_id, quantity, unit_price))

            # Actualizar stock del producto
            save_transaction(product_id=product_id, type="out", quantity=quantity, conn=conn, sale_id=sale_id)
    return sale_id