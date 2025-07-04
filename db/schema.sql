CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    unit TEXT NOT NULL,
    price REAL,
    stock INTEGER,
    stock_low INTEGER,
    active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_variant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    variant_name TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    stock_low INTEGER NOT NULL DEFAULT 0,
    price REAL,
    FOREIGN KEY (product_id) REFERENCES product(id)
);


/* Tablas de clientes y proveedores */
CREATE TABLE IF NOT EXISTS client (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    phone TEXT,
    mail TEXT
);

CREATE TABLE IF NOT EXISTS supplier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    phone TEXT,
    mail TEXT
);

/* Tabla con datos grales de la venta */
CREATE TABLE IF NOT EXISTS sale (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    client_id INTEGER,
    total REAL NOT NULL,
    FOREIGN KEY (client_id) REFERENCES client(id) ON DELETE CASCADE
);

/* Hay muchos detalles_venta por venta, ya que hay uno por producto de la venta */
CREATE TABLE IF NOT EXISTS sale_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER,
    variant_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sale(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variant(id) ON DELETE CASCADE
);

/* Tabla con datos grales de la compra de insumos a proovedores */
CREATE TABLE IF NOT EXISTS purchase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    supplier_id INTEGER,
    total REAL NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES supplier(id) ON DELETE CASCADE
);

/* Hay muchos detalles_compra por compra, ya que hay uno por producto de la compra */
CREATE TABLE IF NOT EXISTS purchase_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER NOT NULL,
    product_id INTEGER,
    variant_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES purchase(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variant(id) ON DELETE CASCADE
);

/* Esta tabla guarda cada movimiento que afecta al stock de un producto. Incluye fecha, tipo, cantidad y una descripción opcional. */
CREATE TABLE IF NOT EXISTS transaction_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    variant_id INTEGER,
    date TEXT NOT NULL,
    type TEXT CHECK(type IN ('in', 'out')) NOT NULL,
    quantity REAL NOT NULL,
    sale_id INTEGER,
    purchase_id INTEGER,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variant(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_id) REFERENCES sale(id) ON DELETE CASCADE,
    FOREIGN KEY (purchase_id) REFERENCES purchase(id) ON DELETE CASCADE
);
