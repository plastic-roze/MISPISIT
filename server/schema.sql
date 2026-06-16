-- Database: pc_assembly
-- PostgreSQL 15+

CREATE TABLE IF NOT EXISTS component_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS components (
    component_id SERIAL PRIMARY KEY,
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
    pc_category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS catalog_builds (
    build_id SERIAL PRIMARY KEY,
    pc_category_id INTEGER NOT NULL REFERENCES pc_categories(pc_category_id),
    build_name VARCHAR(100) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    markup_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS catalog_build_items (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES catalog_builds(build_id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES components(component_id),
    quantity INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clients (
    client_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(client_id),
    build_id INTEGER REFERENCES catalog_builds(build_id),
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('catalog', 'custom')),
    status VARCHAR(20) NOT NULL DEFAULT 'accepted' CHECK (status IN ('accepted', 'assembling', 'ready', 'issued', 'cancelled')),
    total_price DECIMAL(10,2) NOT NULL,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES components(component_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS finances (
    record_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    record_type VARCHAR(20) NOT NULL CHECK (record_type IN ('income', 'expense')),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    record_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert default data
INSERT INTO component_categories (category_name, description) VALUES
('CPU', 'Процессоры'),
('GPU', 'Видеокарты'),
('RAM', 'Оперативная память'),
('Motherboard', 'Материнские платы'),
('Storage', 'Накопители'),
('PSU', 'Блоки питания'),
('Case', 'Корпуса')
ON CONFLICT DO NOTHING;

INSERT INTO pc_categories (category_name, description) VALUES
('Игровой', 'Компьютеры для игр'),
('Офисный', 'Компьютеры для офиса'),
('Рабочая станция', 'Профессиональные рабочие станции')
ON CONFLICT DO NOTHING;

INSERT INTO users (username, password_hash, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1O', 'admin'),
('manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1O', 'manager'),
('operator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1O', 'operator')
ON CONFLICT DO NOTHING;
-- Default password for all: 'password123'
