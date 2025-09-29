from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from app.models import Supplier, Shop, Product, Category, get_db, log_action
from typing import Any, Union
from werkzeug.wrappers import Response

supplier_bp = Blueprint('supplier', __name__)

def supplier_required(f: Any) -> Any:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_authenticated or current_user.role != 'supplier':
            flash('Доступ запрещен', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@supplier_bp.route('/dashboard')
@login_required
@supplier_required
def dashboard():
    supplier = Supplier.get_by_user_id(current_user.id)
    if not supplier:
        flash('Профиль Торговыйа не найден', 'error')
        return redirect(url_for('auth.login'))
    
    shops = Shop.get_by_supplier_id(supplier.id)
    
    db = get_db()
    stats = {
        'shops_count': len(shops),
        'products_count': db.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'pending_requests': db.execute(
            '''SELECT COUNT(*) FROM requests 
               WHERE supplier_id = ? AND status = ?''', 
            (supplier.id, 'pending')
        ).fetchone()[0]
    }
    
    return render_template('supplier/dashboard.html', supplier=supplier, shops=shops, stats=stats)

@supplier_bp.route('/profile')
@login_required
@supplier_required
def profile():
    supplier = Supplier.get_by_user_id(current_user.id)
    if not supplier:
        flash('Профиль Торговыйа не найден', 'error')
        return redirect(url_for('auth.login'))
    
    shops = Shop.get_by_supplier_id(supplier.id)
    
    db = get_db()
    stats = {
        'shops_count': len(shops),
        'products_count': db.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'pending_requests': db.execute(
            '''SELECT COUNT(*) FROM requests 
               WHERE supplier_id = ? AND status = ?''', 
            (supplier.id, 'pending')
        ).fetchone()[0]
    }
    
    return render_template('supplier/profile.html', supplier=supplier, stats=stats)

@supplier_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@supplier_required
def edit_profile():
    supplier = Supplier.get_by_user_id(current_user.id)
    if not supplier:
        flash('Профиль Торговыйа не найден', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form['name']
        info = request.form.get('info', '')
        
        # Обновляем данные Торговыйа
        Supplier.update(supplier.id, name, info)
        log_action(current_user.id, 'update', 'supplier', supplier.id)
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('supplier.profile'))
    
    return render_template('supplier/edit_profile.html', supplier=supplier)

@supplier_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
@supplier_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        from werkzeug.security import check_password_hash, generate_password_hash
        
        # Проверяем текущий пароль
        if not check_password_hash(current_user.password, current_password):
            flash('Текущий пароль введен неверно', 'error')
            return render_template('supplier/change_password.html')
        
        # Проверяем совпадение новых паролей
        if new_password != confirm_password:
            flash('Новые пароли не совпадают', 'error')
            return render_template('supplier/change_password.html')
        
        # Проверяем длину нового пароля
        if len(new_password) < 6:
            flash('Новый пароль должен содержать минимум 6 символов', 'error')
            return render_template('supplier/change_password.html')
        
        # Обновляем пароль
        from app.models import User
        User.update_password(current_user.id, generate_password_hash(new_password))
        log_action(current_user.id, 'update', 'user_password', current_user.id)
        flash('Пароль успешно изменен', 'success')
        return redirect(url_for('supplier.profile'))
    
    return render_template('supplier/change_password.html')

@supplier_bp.route('/shops')
@login_required
@supplier_required
def shops():
    supplier = Supplier.get_by_user_id(current_user.id)
    shops = Shop.get_by_supplier_id(supplier.id)
    return render_template('supplier/shops.html', shops=shops)

@supplier_bp.route('/shops/add', methods=['GET', 'POST'])
@login_required
@supplier_required
def add_shop():
    if request.method == 'POST':
        supplier = Supplier.get_by_user_id(current_user.id)
        name = request.form['name']
        business_type = request.form['business_type']
        info = request.form.get('info', '')
        
        shop_id = Shop.create(supplier.id, name, info, business_type)
        log_action(current_user.id, 'create', 'shop', shop_id)
        flash('Магазин успешно создан', 'success')
        return redirect(url_for('supplier.shops'))
    
    return render_template('supplier/add_shop.html')

@supplier_bp.route('/shops/<int:shop_id>')
@login_required
@supplier_required
def shop_detail(shop_id):
    # Проверяем принадлежность магазина Торговыйу
    supplier = Supplier.get_by_user_id(current_user.id)
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE id = ? AND supplier_id = ?',
        (shop_id, supplier.id)
    ).fetchone()
    
    if not shop:
        flash('Магазин не найден', 'error')
        return redirect(url_for('supplier.shops'))
    
    return render_template('supplier/shop_detail.html', shop=shop)

@supplier_bp.route('/shops/<int:shop_id>/requests')
@login_required
@supplier_required
def shop_requests(shop_id):
    # Проверяем принадлежность магазина Торговыйу
    supplier = Supplier.get_by_user_id(current_user.id)
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE id = ? AND supplier_id = ?',
        (shop_id, supplier.id)
    ).fetchone()
    
    if not shop:
        flash('Магазин не найден', 'error')
        return redirect(url_for('supplier.shops'))
    
    requests = db.execute('''
        SELECT r.*, COUNT(ri.id) as items_count
        FROM requests r
        LEFT JOIN request_items ri ON r.id = ri.request_id
        WHERE r.shop_id = ?
        GROUP BY r.id
        ORDER BY r.created_at DESC
    ''', (shop_id,)).fetchall()
    
    return render_template('supplier/shop_requests.html', shop=shop, requests=requests)

@supplier_bp.route('/shops/<int:shop_id>/requests/create', methods=['GET', 'POST'])
@login_required
@supplier_required
def create_request(shop_id):
    # Проверяем принадлежность магазина Торговыйу
    supplier = Supplier.get_by_user_id(current_user.id)
    db = get_db()
    shop = db.execute(
        'SELECT * FROM shops WHERE id = ? AND supplier_id = ?',
        (shop_id, supplier.id)
    ).fetchone()
    
    if not shop:
        flash('Магазин не найден', 'error')
        return redirect(url_for('supplier.shops'))
    
    if request.method == 'POST':
        # Создаем заявку
        cursor = db.execute(
            'INSERT INTO requests (shop_id, supplier_id) VALUES (?, ?)',
            (shop_id, supplier.id)
        )
        request_id = cursor.lastrowid
        
        # Добавляем товары в заявку
        # Обрабатываем данные в формате products[ID] = quantity
        for key, quantity in request.form.items():
            if key.startswith('products[') and key.endswith(']') and quantity and int(quantity) > 0:
                # Извлекаем product_id из строки вида "products[123]"
                product_id = key[9:-1]  # убираем "products[" и "]"
                db.execute(
                    'INSERT INTO request_items (request_id, product_id, quantity) VALUES (?, ?, ?)',
                    (request_id, int(product_id), int(quantity))
                )
        
        db.commit()
        log_action(current_user.id, 'create', 'request', request_id)
        flash('Заявка успешно создана', 'success')
        return redirect(url_for('supplier.shop_requests', shop_id=shop_id))
    
    # Получаем все глобальные товары созданные админом
    products = Product.get_all()
    return render_template('supplier/create_request.html', shop=shop, products=products)