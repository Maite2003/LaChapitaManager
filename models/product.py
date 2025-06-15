from db.db import get_connection

class Product():
    def __init__(self, name, category, unit, price, stock=0, stock_low=0, id = None):
        self.id = id
        self.name = name
        self.category = category
        self.unit = unit
        self.price = price
        self.stock = stock
        self.stock_low = stock_low

    # Metodo que actualiza el producto en la data base con sus atributos
    # Si no existe el producto en la database (no hay id coincidente), crea una nueva entrada
    def save(self, conn=None):
        if conn is None:
            # Si no se pasa una conexión, se obtiene una nueva
            conn = get_connection()
            conn.isolation_level = 'EXCLUSIVE'
        with conn:  # Usar el contexto para manejar la conexión
            cursor = conn.cursor()
            if self.id:  # Enable WAL mode
                cursor.execute("""UPDATE product SET name=?, category=?, unit=?, price=?, 
                                    stock=?, stock_low=? WHERE id=?
                                """, (self.name, self.category, self.unit, self.price,
                                      self.stock, self.stock_low, self.id))
            else:
                cursor.execute("""INSERT INTO product (name, category, unit, price, 
                                    stock, stock_low)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (self.name, self.category, self.unit, self.price,
                                      self.stock, self.stock_low))
                self.id = cursor.lastrowid



    # Devuelve una lista de todos los productos en la base de datos
    @staticmethod
    def get_all():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM product")
            # Devuelve todas las filas resultantes de haber ejecutado la query de execute
            filas = cursor.fetchall()
            # Devuelve una lista con un producto por fila de filas
        return [Product(*fila[1:], id=fila[0]) for fila in filas]


    # Elimina un producto de la data base por su id
    @staticmethod
    def delete(product_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM product WHERE id=?", (product_id,))



