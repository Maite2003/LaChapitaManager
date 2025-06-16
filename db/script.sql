-- INSERTAR PRODUCTOS
INSERT INTO producto (nombre, tipo, unidad, precio_venta, stock, stock_minimo) VALUES
('Lúpulo Amarillo', 'Insumo', 'kg', 1500.00, 50, 5),
('Malta Pilsen', 'Insumo', 'kg', 800.00, 120, 10),
('Levadura Ale', 'Insumo', 'g', 300.00, 500, 50),
('Botella 500ml', 'Envase', 'unidad', 30.00, 1000, 100),
('Etiqueta Cerveza', 'Material', 'unidad', 5.00, 2000, 500);

-- INSERTAR CLIENTES
INSERT INTO cliente (nombre, apellido, celular, mail) VALUES
('Juan', 'Pérez', '123456789', 'juan.perez@mail.com'),
('María', 'González', '987654321', 'maria.gonzalez@mail.com');

-- INSERTAR PROVEEDORES
INSERT INTO proveedor (nombre, apellido, celular, mail) VALUES
('Carlos', 'Rodríguez', '1122334455', 'carlos.rodriguez@proveedor.com'),
('Laura', 'Martínez', '5566778899', 'laura.martinez@proveedor.com');

-- INSERTAR COMPRAS
INSERT INTO compra (fecha, proveedor_id, total) VALUES
('2025-06-01 10:00:00', 1, 30000.00),
('2025-06-05 15:30:00', 2, 15000.00);

-- DETALLES DE COMPRA
INSERT INTO detalle_compra (compra_id, producto_id, cantidad, precio_unitario) VALUES
(1, 1, 20, 1400.00),
(1, 2, 30, 750.00),
(2, 3, 100, 280.00),
(2, 4, 500, 28.00);

-- INSERTAR VENTAS
INSERT INTO venta (fecha, cliente_id, total) VALUES
('2025-06-10 11:00:00', 1, 45000.00),
('2025-06-12 16:45:00', 2, 22000.00);

-- DETALLES DE VENTA
INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario) VALUES
(1, 1, 15, 1500.00),
(1, 4, 300, 30.00),
(2, 2, 10, 800.00),
(2, 5, 100, 5.00);

-- MOVIMIENTOS DE STOCK (Entradas y salidas)
INSERT INTO movimiento_stock (producto_id, fecha, tipo, cantidad, observacion, venta_id, compra_id) VALUES
(1, '2025-06-01 10:05:00', 'entrada', 20, 'Compra a proveedor Carlos', NULL, 1),
(2, '2025-06-01 10:10:00', 'entrada', 30, 'Compra a proveedor Carlos', NULL, 1),
(3, '2025-06-05 15:35:00', 'entrada', 100, 'Compra a proveedor Laura', NULL, 2),
(4, '2025-06-05 15:40:00', 'entrada', 500, 'Compra a proveedor Laura', NULL, 2),
(1, '2025-06-10 11:10:00', 'salida', 15, 'Venta a cliente Juan', 1, NULL),
(4, '2025-06-10 11:15:00', 'salida', 300, 'Venta a cliente Juan', 1, NULL),
(2, '2025-06-12 16:50:00', 'salida', 10, 'Venta a cliente María', 2, NULL),
(5, '2025-06-12 16:55:00', 'salida', 100, 'Venta a cliente María', 2, NULL);