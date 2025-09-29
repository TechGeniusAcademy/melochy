from flask import Flask
from flask_login import LoginManager
import os
from typing import Optional

def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DATABASE'] = 'app.db'
    
    # Безопасная обработка static_folder
    static_folder = app.static_folder or 'static'
    app.config['UPLOAD_FOLDER'] = os.path.join(static_folder, 'uploads')
    
    # Инициализация Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему'
    login_manager.login_message_category = 'info'
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional['User']:
        return User.get_by_id(int(user_id))
    
    # Регистрация blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.supplier import supplier_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(supplier_bp, url_prefix='/supplier')
    app.register_blueprint(main_bp)
    
    # Обработка закрытия БД
    from app.models import close_db
    
    @app.teardown_appcontext
    def close_db_error(error: Optional[BaseException]) -> None:
        close_db(error)
    
    return app