from models.category import Category
from models.product import Product

class ProductService:
    @staticmethod
    def create_product(data):
        """
        Creates a Product object and saves it to the database.
        Expects a dictionary with keys: name, category, unit, price, stock, stock_low, variants
        """
        product = Product(
            name=data["name"],
            category=data["category"],
            unit=data["unit"],
            price=data["price"],
            stock=data["stock"],
            stock_low=data["stock_low"],
            variants=data.get("variants", [])
        ).save()
        return product

    @staticmethod
    def update_product(data):
        """
        Updates an existing Product using its id.
        Expects a dictionary with all product fields including 'id'.
        """
        product = Product(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            unit=data["unit"],
            price=data["price"],
            stock=data["stock"],
            stock_low=data["stock_low"],
            variants=data["variants"]
        ).save()
        return product

    @staticmethod
    def get_all_products(active=2):
        """
        Returns all products from the database, each with its variants.
        """
        return Product.get_all(active)

    @staticmethod
    def get_product_by_id(product_id):
        """
        Returns a single product by ID, including its variants.
        """
        return Product.get_by_id(product_id)

    @staticmethod
    def delete_product(product_id):
        """
        Deletes a product by ID (and its variants if needed).
        """
        Product.delete(product_id)

    @staticmethod
    def exists_product_name(name):
        """Check if a product name already exists."""
        return Product.exists_name(name)

    @staticmethod
    def count_products_by_category(category_name):
        """Count number of products in a category."""
        return Product.count_by_category(category_name)

    @staticmethod
    def check_stock(items):
        """
        Checks if the stock is sufficient for a list of items.
        Expects a list of tuples (product_id, variant_id, quantity).
        """
        return Product.check_stock(items)

    # ----------- CATEGORY -----------
    @staticmethod
    def get_all_categories():
        return Category.get_all()

    @staticmethod
    def add_category(name):
        if not name.strip():
            raise ValueError("Category name cannot be empty.")
        return Category.add_category(name)

    @staticmethod
    def delete_category_by_id(id):
        return Category.delete_by_id(id)

    @staticmethod
    def rename_category(id, new_name):
        return Category.rename_category(id, new_name)

    @staticmethod
    def get_category_id_by_name(name):
        return Category.get_id_by_name(name)




