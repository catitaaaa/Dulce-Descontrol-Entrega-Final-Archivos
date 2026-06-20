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
    fecha_pedido TEXT DEFAULT CURRENT_DATE, 
    fecha_entrega TEXT NOT NULL,
    entrega TEXT NOT NULL CHECK(entrega IN ('Retiro', 'Domicilio')),
    estado TEXT NOT NULL CHECK(estado IN ('Cotizado', 'Confirmado', 'En producción', 'Entregado', 'Rechazado')),
    precio INTEGER DEFAULT 0,
    resumen TEXT, 
    notas TEXT,
    img TEXT,
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

-- ==========================================
-- DATOS DE PRUEBA (MOCK DATA)
-- ==========================================

INSERT INTO Clientes (nombre, email, telefono) VALUES 
('Ana Martínez', 'ana@email.com', '+56987654321'), 
('Carlos Silva', 'carlos@email.com', '+56912345678');

-- EL STOCK INICIAL DE BODEGA
INSERT INTO Ingredientes (nombre, unidad_medida, stock) VALUES 
('Harina de trigo', 'kg', 3.0),      -- ID 1
('Azúcar blanca', 'kg', 2.0),        -- ID 2
('Huevos', 'unidades', 20.0),        -- ID 3
('Mantequilla', 'kg', 1.0),          -- ID 4
('Chocolate semi-amargo', 'kg', 0.5),-- ID 5
('Queso Crema', 'kg', 1.0),          -- ID 6
('Frambuesas', 'kg', 0.5);           -- ID 7

-- PEDIDOS DE PRUEBA CON LA NUEVA ESTRUCTURA
INSERT INTO Pedidos (id_cliente, fecha_entrega, entrega, estado, precio, resumen, notas, img) VALUES 
(1, '2026-06-25', 'Retiro', 'En producción', 28900, 'Torta Red Velvet (Redonda, 15p)', 'Feliz Cumpleaños Ana', 'https://images.unsplash.com/photo-1616541823729-00fe0aacd32c?w=500&q=80'),
(2, '2026-06-28', 'Domicilio', 'Confirmado', 23000, 'Pie de Limón (Redonda, 15p) | Dir: Los Aromos 123', 'Sin notas', 'pie-limon.jpg'),
(1, '2026-07-02', 'Retiro', 'Rechazado', 30000, '100% Personalizada (Bizcocho: Vainilla) (Cuadrada, 20p)', 'Quiero que sea azul', '');

-- ASIGNAR INGREDIENTES A ESOS PEDIDOS
INSERT INTO Pedido_Ingrediente (id_pedido, id_ingrediente, cantidad_necesaria) VALUES 
(1, 1, 0.4), (1, 2, 0.3), (1, 3, 3.0), (1, 4, 0.2), (1, 6, 2.0), -- Red Velvet
(2, 1, 0.3), (2, 2, 0.1), (2, 3, 3.0), (2, 4, 0.2);              -- Pie de Limón