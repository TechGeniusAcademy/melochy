import sqlite3
from flask import current_app, g
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from typing import Optional, Any, List, Union

def get_db() -> sqlite3.Connection:
    """Получение подключения к базе данных"""
    if 'db' not in g:
        database_path = current_app.config.get('DATABASE', 'app.db')
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e: Optional[BaseException] = None) -> None:
    """Закрытие подключения к базе данных"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def log_action(user_id: int, action: str, entity: str, entity_id: Optional[int] = None) -> None:
    """Логирование действий пользователя"""
    db = get_db()
    db.execute(
        'INSERT INTO logs (user_id, action, entity, entity_id) VALUES (?, ?, ?, ?)',
        (user_id, action, entity, entity_id)
    )
    db.commit()

class User(UserMixin):
    def __init__(self, id: int, email: str, password: str, role: str, 
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        
        if user:
            return User(
                id=user['id'],
                email=user['email'],
                password=user['password'],
                role=user['role'],
                created_at=user['created_at'],
                updated_at=user['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        
        if user:
            return User(
                id=user['id'],
                email=user['email'],
                password=user['password'],
                role=user['role'],
                created_at=user['created_at'],
                updated_at=user['updated_at']
            )
        return None
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)
    
    @staticmethod
    def create(email: str, password: str, role: str) -> Optional[int]:
        db = get_db()
        hashed_password = generate_password_hash(password)
        
        cursor = db.execute(
            'INSERT INTO users (email, password, role) VALUES (?, ?, ?)',
            (email, hashed_password, role)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_all():
        db = get_db()
        users = db.execute(
            'SELECT * FROM users ORDER BY created_at DESC'
        ).fetchall()
        
        return [User(
            id=user['id'],
            email=user['email'],
            password=user['password'],
            role=user['role'],
            created_at=user['created_at'],
            updated_at=user['updated_at']
        ) for user in users]
    
    @staticmethod
    def update_password(user_id, password_hash):
        db = get_db()
        db.execute(
            'UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (password_hash, user_id)
        )
        db.commit()
        return True

class Supplier:
    def __init__(self, id: int, user_id: int, name: str, info: Optional[str] = None, 
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.info = info
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(user_id: int, name: str, info: Optional[str] = None) -> Optional[int]:
        db = get_db()
        cursor = db.execute(
            'INSERT INTO suppliers (user_id, name, info) VALUES (?, ?, ?)',
            (user_id, name, info)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_user_id(user_id: int) -> Optional['Supplier']:
        db = get_db()
        supplier = db.execute(
            'SELECT * FROM suppliers WHERE user_id = ?', (user_id,)
        ).fetchone()
        
        if supplier:
            return Supplier(
                id=supplier['id'],
                user_id=supplier['user_id'],
                name=supplier['name'],
                info=supplier['info'],
                created_at=supplier['created_at'],
                updated_at=supplier['updated_at']
            )
        return None
    
    @staticmethod
    def get_by_id(supplier_id: int) -> Optional['Supplier']:
        db = get_db()
        supplier = db.execute(
            'SELECT * FROM suppliers WHERE id = ?', (supplier_id,)
        ).fetchone()
        
        if supplier:
            return Supplier(
                id=supplier['id'],
                user_id=supplier['user_id'],
                name=supplier['name'],
                info=supplier['info'],
                created_at=supplier['created_at'],
                updated_at=supplier['updated_at']
            )
        return None
    
    @staticmethod
    def update(supplier_id: int, name: str, info: Optional[str] = None) -> bool:
        db = get_db()
        db.execute(
            'UPDATE suppliers SET name = ?, info = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (name, info, supplier_id)
        )
        db.commit()
        return True
    
    @staticmethod
    def get_all():
        db = get_db()
        suppliers = db.execute(
            '''SELECT s.*, u.email 
               FROM suppliers s 
               JOIN users u ON s.user_id = u.id 
               ORDER BY s.created_at DESC'''
        ).fetchall()
        
        return suppliers
    
    @staticmethod
    def update(supplier_id, name, info=None):
        db = get_db()
        db.execute(
            'UPDATE suppliers SET name = ?, info = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (name, info, supplier_id)
        )
        db.commit()
        return True

class Shop:
    def __init__(self, id, supplier_id, name, info=None, business_type=None, created_at=None, updated_at=None):
        self.id = id
        self.supplier_id = supplier_id
        self.name = name
        self.info = info
        self.business_type = business_type
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(supplier_id, name, info=None, business_type=None):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO shops (supplier_id, name, info, business_type) VALUES (?, ?, ?, ?)',
            (supplier_id, name, info, business_type)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_supplier_id(supplier_id):
        db = get_db()
        shops = db.execute(
            'SELECT * FROM shops WHERE supplier_id = ? ORDER BY created_at DESC',
            (supplier_id,)
        ).fetchall()
        
        return [Shop(
            id=shop['id'],
            supplier_id=shop['supplier_id'],
            name=shop['name'],
            info=shop['info'],
            business_type=shop['business_type'],
            created_at=shop['created_at'],
            updated_at=shop['updated_at']
        ) for shop in shops]
    
    @staticmethod
    def get_all():
        db = get_db()
        shops = db.execute(
            '''SELECT sh.*, s.name as supplier_name 
               FROM shops sh 
               JOIN suppliers s ON sh.supplier_id = s.id 
               ORDER BY sh.created_at DESC'''
        ).fetchall()
        
        return shops
    
    @staticmethod
    def update(shop_id, name, info=None):
        db = get_db()
        db.execute(
            'UPDATE shops SET name = ?, info = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (name, info, shop_id)
        )
        db.commit()
        return True
    
    @staticmethod
    def delete(shop_id):
        db = get_db()
        db.execute('DELETE FROM shops WHERE id = ?', (shop_id,))
        db.commit()
        return True
    
    @staticmethod
    def get_by_id(shop_id):
        db = get_db()
        shop = db.execute(
            'SELECT * FROM shops WHERE id = ?',
            (shop_id,)
        ).fetchone()
        
        if shop:
            return Shop(
                id=shop['id'],
                supplier_id=shop['supplier_id'],
                name=shop['name'],
                info=shop['info'],
                business_type=shop['business_type'],
                created_at=shop['created_at'],
                updated_at=shop['updated_at']
            )
        return None

class Category:
    def __init__(self, id, name, description=None, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_all():
        db = get_db()
        categories = db.execute(
            'SELECT * FROM categories ORDER BY name'
        ).fetchall()
        
        return [Category(
            id=cat['id'],
            name=cat['name'],
            description=cat['description'],
            created_at=cat['created_at'],
            updated_at=cat['updated_at']
        ) for cat in categories]
    
    @staticmethod
    def create(name, description=None):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO categories (name, description) VALUES (?, ?)',
            (name, description)
        )
        db.commit()
        return cursor.lastrowid

class Product:
    @staticmethod
    def delete(product_id):
        """Удалить товар по ID"""
        db = get_db()
        db.execute('DELETE FROM products WHERE id = ?', (product_id,))
        db.commit()
    def __init__(self, id, category_id, name, description, price, 
                 wholesale_price=None, image_url=None, 
                 created_at=None, updated_at=None):
        self.id = id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.price = price
        self.wholesale_price = wholesale_price
        self.image_url = image_url
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def create(category_id, name, description, price, 
               wholesale_price=None, image_url=None):
        """Создает глобальный товар (только админ)"""
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO products (category_id, name, description, 
                                   price, wholesale_price, image_url) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (category_id, name, description, price, wholesale_price, image_url)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_all():
        """Получить все глобальные товары"""
        db = get_db()
        products = db.execute(
            '''SELECT p.*, c.name as category_name 
               FROM products p 
               LEFT JOIN categories c ON p.category_id = c.id 
               ORDER BY p.created_at DESC'''
        ).fetchall()
        
        return products
    
    @staticmethod
    def get_by_category(category_id=None):
        """Получить товары по категории"""
        db = get_db()
        if category_id:
            products = db.execute(
                '''SELECT p.*, c.name as category_name 
                   FROM products p 
                   LEFT JOIN categories c ON p.category_id = c.id 
                   WHERE p.category_id = ?
                   ORDER BY p.name''',
                (category_id,)
            ).fetchall()
        else:
            products = db.execute(
                '''SELECT p.*, c.name as category_name 
                   FROM products p 
                   LEFT JOIN categories c ON p.category_id = c.id 
                   ORDER BY p.name'''
            ).fetchall()
        
        return products
    
    @staticmethod
    def get_by_id(product_id):
        """Получить товар по ID"""
        db = get_db()
        product = db.execute(
            '''SELECT p.*, c.name as category_name 
               FROM products p 
               LEFT JOIN categories c ON p.category_id = c.id 
               WHERE p.id = ?''',
            (product_id,)
        ).fetchone()
        
        return product
    
    @staticmethod
    def update(product_id, category_id, name, description, price, 
               wholesale_price=None, image_url=None):
        """Обновить товар"""
        db = get_db()
        db.execute(
            '''UPDATE products 
               SET category_id = ?, name = ?, description = ?, 
                   price = ?, wholesale_price = ?, image_url = ?, 
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (category_id, name, description, price, wholesale_price, image_url, product_id)
        )
        db.commit()


class Request:
    def __init__(self, id, shop_id, supplier_id, status='pending', 
                 created_at=None, updated_at=None):
        self.id = id
        self.shop_id = shop_id
        self.supplier_id = supplier_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_by_id(request_id):
        """Получить заявку по ID"""
        db = get_db()
        request = db.execute(
            '''SELECT r.*, s.name as shop_name, sup.name as supplier_name
               FROM requests r
               JOIN shops s ON r.shop_id = s.id
               JOIN suppliers sup ON r.supplier_id = sup.id
               WHERE r.id = ?''',
            (request_id,)
        ).fetchone()
        return request
    
    @staticmethod
    def get_items(request_id):
        """Получить товары заявки"""
        db = get_db()
        items = db.execute(
            '''SELECT ri.*, p.name as product_name, p.description as product_description, 
                      p.price, p.wholesale_price, p.image_url
               FROM request_items ri
               JOIN products p ON ri.product_id = p.id
               WHERE ri.request_id = ?
               ORDER BY p.name''',
            (request_id,)
        ).fetchall()
        return items
    
    @staticmethod
    def update_status(request_id, status):
        """Обновить статус заявки"""
        db = get_db()
        db.execute(
            'UPDATE requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (status, request_id)
        )
        db.commit()
    
    @staticmethod
    def add_item(request_id, product_id, quantity):
        """Добавить товар в заявку"""
        db = get_db()
        # Проверяем, есть ли уже такой товар в заявке
        existing = db.execute(
            'SELECT id, quantity FROM request_items WHERE request_id = ? AND product_id = ?',
            (request_id, product_id)
        ).fetchone()
        
        if existing:
            # Обновляем количество
            db.execute(
                'UPDATE request_items SET quantity = ? WHERE id = ?',
                (quantity, existing['id'])
            )
        else:
            # Добавляем новый товар
            db.execute(
                'INSERT INTO request_items (request_id, product_id, quantity) VALUES (?, ?, ?)',
                (request_id, product_id, quantity)
            )
        db.commit()
    
    @staticmethod
    def remove_item(request_id, product_id):
        """Удалить товар из заявки"""
        db = get_db()
        db.execute(
            'DELETE FROM request_items WHERE request_id = ? AND product_id = ?',
            (request_id, product_id)
        )
        db.commit()
    
    @staticmethod
    def delete(request_id):
        """Удалить заявку по ID"""
        db = get_db()
        # Сначала удаляем связанные позиции заявки
        db.execute('DELETE FROM request_items WHERE request_id = ?', (request_id,))
        # Потом удаляем саму заявку
        db.execute('DELETE FROM requests WHERE id = ?', (request_id,))
        db.commit()