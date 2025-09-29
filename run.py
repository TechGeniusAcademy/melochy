from app import create_app
from init_db import init_db
import os

if __name__ == '__main__':
    # Инициализация базы данных
    if not os.path.exists('app.db'):
        init_db()
    
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)