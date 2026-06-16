-- SQLite Database Schema: pc_assembly.db

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS component_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS components (
    component_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES component_categories(category_id),
    component_name VARCHAR(100) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    specifications TEXT,
    price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    quantity_in_stock INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pc_categories (
    pc_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS catalog_builds (
    build_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pc_category_id INTEGER NOT NULL REFERENCES pc_categories(pc_category_id),
    build_name VARCHAR(100) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    markup_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS catalog_build_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id INTEGER NOT NULL REFERENCES catalog_builds(build_id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES components(component_id),
    quantity INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL REFERENCES clients(client_id),
    build_id INTEGER REFERENCES catalog_builds(build_id),
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('catalog', 'custom')),
    status VARCHAR(20) NOT NULL DEFAULT 'accepted' CHECK (status IN ('accepted', 'assembling', 'ready', 'issued', 'cancelled')),
    total_price DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES components(component_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS finances (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(order_id),
    record_type VARCHAR(20) NOT NULL CHECK (record_type IN ('income', 'expense')),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    record_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Default data
INSERT OR IGNORE INTO component_categories (category_name, description) VALUES
('CPU', 'Процессоры'),
('GPU', 'Видеокарты'),
('RAM', 'Оперативная память'),
('Motherboard', 'Материнские платы'),
('Storage', 'Накопители'),
('PSU', 'Блоки питания'),
('Case', 'Корпуса');

INSERT OR IGNORE INTO pc_categories (category_name, description) VALUES
('Игровой', 'Компьютеры для игр'),
('Офисный', 'Компьютеры для офиса'),
('Рабочая станция', 'Профессиональные рабочие станции');

INSERT OR IGNORE INTO users (username, password_hash, role) VALUES
('admin', '$2b$12$Q8e5SZOpahFixJyy0MM8Pey9WQ9Ab3BcGyp6JcP1IEgD0zMoClTCq', 'admin'),
('manager', '$2b$12$Q8e5SZOpahFixJyy0MM8Pey9WQ9Ab3BcGyp6JcP1IEgD0zMoClTCq', 'manager'),
('operator', '$2b$12$Q8e5SZOpahFixJyy0MM8Pey9WQ9Ab3BcGyp6JcP1IEgD0zMoClTCq', 'operator');
-- Default password for all: 'password123'

-- Sample clients
INSERT OR IGNORE INTO clients (first_name, last_name, email, phone) VALUES
('Иван', 'Иванов', 'ivan@example.com', '+79990000001'),
('Петр', 'Петров', 'petr@example.com', '+79990000002'),
('Сергей', 'Сергеев', 'sergey@example.com', '+79990000003');

-- Sample components
INSERT OR IGNORE INTO components (category_id, component_name, brand, model, specifications, price, selling_price, quantity_in_stock) VALUES
(1, 'Intel Core i9-13900K', 'Intel', 'i9-13900K', '24 ядра, 32 потока, 5.8 GHz', 45000.00, 52000.00, 15),
(1, 'Intel Core i7-13700K', 'Intel', 'i7-13700K', '16 ядер, 24 потока, 5.4 GHz', 35000.00, 42000.00, 8),
(1, 'AMD Ryzen 9 7950X', 'AMD', '7950X', '16 ядер, 32 потока, 5.7 GHz', 48000.00, 55000.00, 12),
(2, 'NVIDIA RTX 4090', 'NVIDIA', 'RTX 4090', '24 GB GDDR6X', 120000.00, 145000.00, 5),
(2, 'NVIDIA RTX 4080', 'NVIDIA', 'RTX 4080', '16 GB GDDR6X', 85000.00, 100000.00, 8),
(2, 'AMD RX 7900 XTX', 'AMD', 'RX 7900 XTX', '24 GB GDDR6', 75000.00, 90000.00, 10),
(3, 'DDR5 32GB 5600MHz', 'Corsair', 'Vengeance', '2x16GB, CL36', 8000.00, 12000.00, 25),
(3, 'DDR5 64GB 6000MHz', 'G.Skill', 'Trident Z5', '2x32GB, CL30', 18000.00, 25000.00, 15),
(4, 'ASUS ROG Maximus Z790', 'ASUS', 'Maximus Z790', 'LGA1700, DDR5, WiFi 6E', 25000.00, 35000.00, 7),
(4, 'MSI MAG B760 Tomahawk', 'MSI', 'B760', 'LGA1700, DDR5', 12000.00, 18000.00, 12),
(5, 'Samsung 990 Pro 2TB', 'Samsung', '990 Pro', 'NVMe PCIe 4.0, 7450 MB/s', 10000.00, 15000.00, 20),
(5, 'WD Black SN850X 1TB', 'WD', 'SN850X', 'NVMe PCIe 4.0, 7300 MB/s', 6000.00, 9000.00, 30),
(6, 'Corsair RM1000x', 'Corsair', 'RM1000x', '1000W, 80+ Gold, модульный', 8000.00, 12000.00, 18),
(6, 'be quiet! Dark Power 13', 'be quiet!', 'Dark Power 13', '850W, 80+ Titanium', 12000.00, 18000.00, 10),
(7, 'NZXT H7 Flow', 'NZXT', 'H7 Flow', 'ATX, tempered glass, 2x140mm', 7000.00, 10000.00, 15),
(7, 'Fractal Design North', 'Fractal', 'North', 'ATX, wood panel, mesh', 9000.00, 13000.00, 8);
