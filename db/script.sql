PRAGMA foreign_keys = ON;

CREATE TABLE Clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    email TEXT UNIQUE
);

CREATE TABLE Ingredientes (
    id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    unidad_medida TEXT NOT NULL,
    stock REAL DEFAULT 0.0
);

CREATE TABLE Pedidos (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    fecha_pedido TEXT NOT NULL, 
    fecha_entrega TEXT NOT NULL,
    estado TEXT NOT NULL CHECK(estado IN ('Cotizado', 'Confirmado', 'En producción', 'Entregado')),
    monto_total INTEGER DEFAULT 0,
    detalles TEXT, 
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Pedido_Ingrediente (
    id_pedido INTEGER NOT NULL,
    id_ingrediente INTEGER NOT NULL,
    cantidad_necesaria REAL NOT NULL,
    PRIMARY KEY (id_pedido, id_ingrediente),
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_ingrediente) REFERENCES Ingredientes(id_ingrediente) ON DELETE CASCADE
);

-- DATOS DE PRUEBA
INSERT INTO Clientes (nombre, email) VALUES 
('Ana Martínez', 'ana@email.com'), ('Carlos Silva', 'carlos@email.com');

-- EL STOCK INICIAL DE MARTINA (IDs del 1 al 7)
INSERT INTO Ingredientes (nombre, unidad_medida, stock) VALUES 
('Harina de trigo', 'kg', 3.0),      -- ID 1
('Azúcar blanca', 'kg', 2.0),        -- ID 2
('Huevos', 'unidades', 20.0),        -- ID 3
('Mantequilla', 'kg', 1.0),          -- ID 4
('Chocolate semi-amargo', 'kg', 0.5),-- ID 5
('Queso Crema', 'kg', 1.0),          -- ID 6
('Frambuesas', 'kg', 0.5);           -- ID 7

INSERT INTO Pedidos (id_cliente, fecha_pedido, fecha_entrega, estado, monto_total, detalles) VALUES 
(1, '2026-06-01', '2026-06-11', 'En producción', 25000, 'Torta de Chocolate | Notas: Ninguno'),
(2, '2026-06-05', '2026-06-12', 'Confirmado', 18000, 'Pie de Limón | Notas: Sin azúcar');

-- Asignar ingredientes a esos pedidos iniciales
INSERT INTO Pedido_Ingrediente (id_pedido, id_ingrediente, cantidad_necesaria) VALUES 
(1, 1, 1.0), (1, 3, 5.0), (1, 5, 0.5), -- Torta de chocolate usa harina, huevos, chocolate
(2, 1, 0.5), (2, 3, 3.0), (2, 4, 0.2); -- Pie de limón usa harina, huevos, mantequilla