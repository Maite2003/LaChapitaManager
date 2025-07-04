from datetime import datetime

from models.sale import Sale
from models.purchase import Purchase

class TransactionsService:
    # --------- SALES ----------
    @staticmethod
    def get_all_sales(start_date=None, end_date=None):
        if start_date: start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y-%m-%d") # Convert the date to ISO format
        if end_date: end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        return Sale.get_all(start_date, end_date)

    @staticmethod
    def get_sale_by_id(sale_id):
        if not sale_id or sale_id < 0:
            return None
        return Sale.get_by_id(sale_id)

    @staticmethod
    def save_sale(sale_id, items, client_id, date):
        date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d") # Convert the date to ISO format
        sale = Sale(id=sale_id, items=items, client_id=client_id, date=date)
        return sale.save()

    @staticmethod
    def delete_sale(sale_id):
        if not sale_id or sale_id < 0:
            raise ValueError("Invalid sale ID")
        Sale.delete(sale_id)

    @staticmethod
    def get_top5_products(start_date=None, end_date=None):
        """
        Get the top 5 products sold within a specified date range.
        If no dates are provided, it returns the top 5 products without filtering.
        """
        if start_date: start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        if end_date: end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        return Sale.get_top5_products(start_date, end_date)

    @staticmethod
    def get_sales_by_categories(start_date=None, end_date=None):
        """
        Get the total sales amount by category within a specified date range.
        If no dates are provided, it returns the total sales amount by category without filtering.
        """
        if start_date: start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        if end_date: end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        return Sale.get_sales_by_categories(start_date=start_date, end_date=end_date)

    # --------- PURCHASES ----------
    @staticmethod
    def get_all_purchases(start_date=None, end_date=None):
        if start_date: start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        if end_date: end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        return Purchase.get_all(start_date, end_date)

    @staticmethod
    def get_purchase_by_id(purchase_id):
        if not purchase_id or purchase_id < 0:
            return None
        return Purchase.get_by_id(purchase_id)

    @staticmethod
    def save_purchase(purchase_id, items, supplier_id, date):
        date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d") # Convert the date to ISO format
        purchase = Purchase(id=purchase_id, items=items, supplier_id=supplier_id, date=date)
        return purchase.save()

    @staticmethod
    def delete_purchase(purchase_id):
        if not purchase_id or purchase_id < 0:
            raise ValueError("Invalid sale ID")
        Purchase.delete(purchase_id)

    # --------- BOTH ----------

    @staticmethod
    def get_totals(start_date=None, end_date=None):
        """
        Get the total sales and purchase amount within a specified date range.
        If no dates are provided, it returns the total sales amount without filtering.
        """
        if start_date: start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        if end_date: end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        return Sale.get_total(start_date, end_date), Purchase.get_total(start_date, end_date)