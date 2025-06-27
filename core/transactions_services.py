from models.sale import Sale
from models.purchase import Purchase

class TransactionsService:
    # --------- SALES ----------
    @staticmethod
    def get_all_sales():
        return Sale.get_all()

    @staticmethod
    def get_sale_by_id(sale_id):
        if not sale_id or sale_id < 0:
            return None
        return Sale.get_by_id(sale_id)

    @staticmethod
    def save_sale(sale_id, items, client_id, date):
        sale = Sale(id=sale_id, items=items, client_id=client_id, date=date)
        return sale.save()

    @staticmethod
    def delete_sale(sale_id):
        if not sale_id or sale_id < 0:
            raise ValueError("Invalid sale ID")
        Sale.delete(sale_id)

    # --------- PURCHASES ----------
    @staticmethod
    def get_all_purchases():
        return Purchase.get_all()

    @staticmethod
    def get_purchase_by_id(purchase_id):
        if not purchase_id or purchase_id < 0:
            return None
        return Purchase.get_by_id(purchase_id)

    @staticmethod
    def save_purchase(purchase_id, items, supplier_id, date):
        purchase = Purchase(id=purchase_id, items=items, supplier_id=supplier_id, date=date)
        return purchase.save()

    @staticmethod
    def delete_purchase(purchase_id):
        if not purchase_id or purchase_id < 0:
            raise ValueError("Invalid sale ID")
        Purchase.delete(purchase_id)
