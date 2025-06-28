from db.db import get_connection
from datetime import datetime

from models.product import Product

def save_transaction(product_id, quantity, type, obs='', variant_id=None,date = datetime.now().strftime('%d-%m-%Y'), sale_id=None, purchase_id=None, conn=None):
    if type not in ["in", "out"]:
        raise ValueError("Tipo de movimiento debe ser 'in' o 'out'")

    if type == "in":
        Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=quantity, type="in", conn=conn)
    else:
        Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=quantity, type="out", conn=conn)

    # registrar movimiento en la base de datos de movimientos
    if conn is None:
        conn = get_connection()
        conn.isolation_level = 'EXCLUSIVE'
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transaction_stock (product_id, variant_id, date, type, quantity, obs, sale_id, purchase_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_id, variant_id, datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d"), type, quantity, obs, sale_id, purchase_id))


def update_transaction(product_id, variant_id, new_q, type, sale_id=None, purchase_id=None, conn=None):
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM transaction_stock "
                       "WHERE product_id = ? "
                       "AND (variant_id = ? OR variant_id IS NULL)"
                       "AND (sale_id = ? OR sale_id IS NULL) "
                       "AND (purchase_id = ? OR purchase_id IS NULL) "
                       "AND type = ?", (product_id, variant_id, sale_id, purchase_id, type))
        old_amount = cursor.fetchone()

        cursor.execute("UPDATE transaction_stock SET quantity = ? "
                       "WHERE product_id = ? "
                       "AND (variant_id = ? OR variant_id IS NULL) "
                       "AND (sale_id = ? OR sale_id IS NULL)"
                       "AND (purchase_id = ? OR purchase_id IS NULL)"
                       "AND type = ?", (new_q, product_id, variant_id, sale_id, purchase_id, type))

        if sale_id:
            if old_amount[0] > new_q: # Somebody returned
                Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=old_amount[0] - new_q, type="int", conn=conn)
            else: # Sold more
                Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=new_q - old_amount[0], type="out", conn=conn)
        elif purchase_id:
            if old_amount[0] > new_q: # I returned some, I got less
                Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=old_amount[0] - new_q, type="out", conn=conn)
            else: # I bought more of the same
                Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=new_q - old_amount[0], type="in", conn=conn)


def delete_transaction(product_id, variant_id, quantity, type, sale_id=None, purchase_id=None, conn=None):
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transaction_stock WHERE product_id = ? AND variant_id = ? AND sale_id = ? AND type = ?", (product_id, variant_id, sale_id, type))
        transaction = cursor.fetchone()

        if not transaction:
            raise ValueError("Transacción no encontrada")

        if type == "in": # Deleted a purchase, stock decreases
            Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=quantity, type="out", conn=conn)
        else: # Deleted a sale, stock increases
            Product.edit_stock(product_id=product_id, variant_id=variant_id, quantity=quantity, type="in", conn=conn)
        cursor.execute("DELETE FROM transaction_stock WHERE product_id = ? AND variant_id = ? AND sale_id = ? AND purchase_id = ?", (product_id, variant_id, sale_id, purchase_id))

def get_all(start_date, end_date, type='all'):
    if type not in ['all', 'in', 'out']:
        raise ValueError("Tipo debe ser 'all', 'in' o 'out'")

    with get_connection() as conn:
        cursor = conn.cursor()

        if start_date is None or end_date is None:
            if type == 'all':
                cursor.excecute("SELECT * FROM transaction_stock")
            else:
                cursor.execute("SELECT * FROM transaction_stock WHERE type = ?", (type,))
        else:
            if type == 'all':
                cursor.excecute("SELECT * FROM transaction_stock WHERE date BETWEEN ? AND ?", (start_date, end_date))
            else:
                cursor.execute("SELECT * FROM transaction_stock WHERE type = ? AND date BETWEEN ? AND ?", (type, start_date, end_date))

        transactions = cursor.fetchall()
        transactions = [{
            'id': row[0],
            'product_id': row[1],
            'variant_id': row[2],
            'date': datetime.strptime(row[3], "%Y-%m-%d").strftime("%d-%m-%Y"),
            'type': row[4],
            'quantity': row[5],
            'obs': row[6],
            'sale_id': row[7],
            'purchase_id': row[8]
        } for row in transactions]