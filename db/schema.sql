DROP TABLE IF EXISTS product;
CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id TEXT NOT NULL,
    unit TEXT NOT NULL,
    price REAL NOT NULL,
    stock REAL NOT NULL,
    stock_low REAL NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(id)
);

DROP TABLE IF EXISTS category;
CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

/* Esta tabla guarda cada movimiento que afecta al stock de un producto. Incluye fecha, tipo, cantidad y una descripción opcional. */
DROP TABLE IF EXISTS transaction_stock;
CREATE TABLE IF NOT EXISTS transaction_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    type TEXT CHECK(type IN ('in', 'out')) NOT NULL,
    quantity REAL NOT NULL,
    obs TEXT,
    sale_id INTEGER,
    purchase_id INTEGER,
    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (sale_id) REFERENCES sale(id),
    FOREIGN KEY (purchase_id) REFERENCES purchase(id)
);

/* Tabla con datos grales de la venta */
DROP TABLE IF EXISTS sale;
CREATE TABLE IF NOT EXISTS sale (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    client_id INTEGER,
    total REAL NOT NULL,
    FOREIGN KEY (client_id) REFERENCES client(id)
);

/* Hay muchos detalles_venta por venta, ya que hay uno por producto de la venta */
DROP TABLE IF EXISTS sale_detail;
CREATE TABLE IF NOT EXISTS sale_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sale(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
);

/* Tabla con datos grales de la compra de insumos a proovedores */
DROP TABLE IF EXISTS purchase;
CREATE TABLE IF NOT EXISTS purchase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    supplier_id INTEGER,
    total REAL NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES supplier(id)
);

/* Hay muchos detalles_compra por compra, ya que hay uno por producto de la compra */
DROP TABLE IF EXISTS purchase_detail;
CREATE TABLE IF NOT EXISTS detalle_compra (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES purchase(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
);

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

/* VISTAS */

/* Vista general movimientos */
DROP VIEW IF EXISTS view_transactions_stock;
CREATE VIEW IF NOT EXISTS view_transactions_stock AS
SELECT
    ms.id AS mov_id,
    ms.date,
    ms.type,
    ms.quantity,
    ms.obs,
    p.name AS product,
    ms.sale_id,
    ms.purchase_id,

    CASE
        WHEN ms.sale_id IS NOT NULL THEN 'sale'
        WHEN ms.purchase_id IS NOT NULL THEN 'purchase'
        ELSE 'manual'
    END AS origin,

    COALESCE(ms.sale_id, ms.purchase_id, NULL) AS op_id

FROM transaction_stock ms
JOIN product p ON ms.product_id = p.id
ORDER BY ms.date DESC;