from models.stock import save_transaction
from db.db import get_connection
from datetime import datetime

def save_sale(items, client, date = datetime.now().isoformat(timespec="seconds")):
    """
    items = lista de tuplas (product_id, variant_id, quantity, unit_price)
    """
    total = sum(quantity * price for _, _, quantity, price in items)

    with get_connection() as conn:
        cursor = conn.cursor()

        # Registrar la venta
        cursor.execute("""
            INSERT INTO sale (date, client_id, total)
            VALUES (?, ?, ?)
        """, (date, client, total))

        sale_id = cursor.lastrowid

        # Registrar cada item de la venta
        for product_id, variant_id, quantity, unit_price in items:
            cursor.execute("""
                INSERT INTO sale_detail (sale_id, product_id, variant_id, quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
            """, (sale_id, product_id, variant_id, quantity, unit_price))

            # Actualizar stock del producto
            save_transaction(product_id=product_id, variant_id=variant_id, type="out", quantity=quantity, conn=conn, sale_id=sale_id)
    return sale_id


@staticmethod
def load_sale_details(sale_id):
    with get_connection() as conn:
        cur = conn.cursor()

        # Obtener datos generales de la venta
        cur.execute("""
               SELECT sale.date, client.name, client.surname, sale.total
               FROM sale
               LEFT JOIN client ON sale.client_id = client.id
               WHERE sale.id = ?
           """, (sale_id,))
        general_info = cur.fetchone()
        if general_info is None:
            general_info = ("Sin fecha", "Sin nombre", "Sin apellido", 0.0)


        # Obtener detalles de productos
        cur.execute("""
               SELECT product.name, sd.quantity, sd.unit_price
               FROM sale_detail sd
               JOIN product ON product.id = sd.product_id
               WHERE sd.sale_id = ?
           """, (sale_id,))
        product_details = cur.fetchall()

        # Validate product_details and ensure it's a list
        if not product_details:
            product_details = []

    return {
        "general_info": general_info,  # (date, name, surname, total)
        "product_details": product_details  # List of (title, quantity, unit_price)
    }

def get_all():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sale.id, sale.date, client.name, client.surname, sale.total
            FROM sale
            LEFT JOIN client ON sale.client_id = client.id
            ORDER BY sale.date DESC
        """)
        sales = cursor.fetchall()

    return [
        {
            "id": row[0],
            "date": row[1],
            "client": f"{row[2]} {row[3]}" if row[2] else "Sin cliente",
            "total": row[4]
        }
        for row in sales
    ]