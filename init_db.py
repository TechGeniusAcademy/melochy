import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_db():
    """Инициализация базы данных"""
    if os.path.exists('app.db'):
        return
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Создание таблиц
    cursor.executescript('''
        -- Пользователи
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'supplier')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Торговыйи
        CREATE TABLE suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        -- Магазины
        CREATE TABLE shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        );
        
        -- Категории товаров
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Товары (глобальные для всех магазинов)
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            wholesale_price DECIMAL(10,2),
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        );
        
        -- Заказы
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'cancelled')),
            total_price DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        );
        
        -- Позиции заказов
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
        
        -- Заявки от магазинов
        CREATE TABLE requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            supplier_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        );
        
        -- Позиции заявок
        CREATE TABLE request_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (request_id) REFERENCES requests (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
        
        -- Логи действий
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            entity TEXT NOT NULL,
            entity_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        -- Триггеры для обновления updated_at
        CREATE TRIGGER update_users_timestamp 
        AFTER UPDATE ON users 
        BEGIN 
            UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
        END;
        
        CREATE TRIGGER update_suppliers_timestamp 
        AFTER UPDATE ON suppliers 
        BEGIN 
            UPDATE suppliers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
        END;
        
        CREATE TRIGGER update_shops_timestamp 
        AFTER UPDATE ON shops 
        BEGIN 
            UPDATE shops SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
        END;
        
        CREATE TRIGGER update_categories_timestamp 
        AFTER UPDATE ON categories 
        BEGIN 
            UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
        END;
        
        CREATE TRIGGER update_products_timestamp 
        AFTER UPDATE ON products 
        BEGIN 
            UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
        END;
        
        CREATE TRIGGER update_orders_timestamp 
        AFTER UPDATE ON orders 
        BEGIN 
            UPDATE orders SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
        END;
        
        CREATE TRIGGER update_requests_timestamp 
        AFTER UPDATE ON requests 
        BEGIN 
            UPDATE requests SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
        END;
    ''')
    
    # Создание админа по умолчанию
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT INTO users (email, password, role) 
        VALUES ('admin@example.com', ?, 'admin')
    ''', (admin_password,))
    
    # Создание тестовых категорий
    categories = [
        ('Электроника', 'Электронные товары и гаджеты'),
        ('Одежда', 'Одежда и аксессуары'),
        ('Продукты', 'Продукты питания'),
        ('Дом и сад', 'Товары для дома и сада'),
        ('Спорт', 'Спортивные товары')
    ]
    
    cursor.executemany('''
        INSERT INTO categories (name, description) VALUES (?, ?)
    ''', categories)
    
    conn.commit()
    conn.close()
    print("База данных инициализирована успешно!")

if __name__ == '__main__':
    init_db()