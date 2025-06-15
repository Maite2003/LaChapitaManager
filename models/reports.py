from db.db import get_connection

def get_transations():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, type, product, quantity, origin, op_id, obs FROM view_transactions_stock")
        movimientos = cursor.fetchall()

    for mov in movimientos:
        print(
            f"{mov['date']} | {mov['type'].upper():7} | {mov['product']:20} | {mov['quantity']:>5} | {mov['origin']:7} #{mov['op_id'] or ''} | {mov['obs']}")


def get_sales():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, product, quantity, origin, op_id, obs
            FROM view_transactions_stock
            WHERE type = 'out'
            ORDER BY date DESC
        """)
        outs = cursor.fetchall()

        print("\n=== SALIDAS ===")
        for s in outs:
            print(
                f"{s['date']} | {s['product']:20} | -{s['quantity']:>5} | {s['origin']:7} #{s['op_id'] or ''} | {s['obs']}")

def get_purchases():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, product, quantity, origin, op_id, obs
            FROM view_transactions_stock
            WHERE type = 'in'
            ORDER BY date DESC
        """)
        ins = cursor.fetchall()

        print("\n=== ENTRADAS ===")
        for s in ins:
            print(f"{s['date']} | {s['product']:20} | +{s['quantity']:>5} | {s['origin']:7} #{s['op_id'] or ''} | {s['obs']}")





