# Инструкция по деплою проекта на Ubuntu сервер

## Подготовка проекта к деплою

### 1. Создание файла конфигурации для продакшена

Создайте файл `config.py` для настроек продакшена:

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # Для продакшена лучше использовать PostgreSQL
    # DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://user:pass@localhost/dbname'

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 2. Обновление requirements.txt

Убедитесь, что все зависимости указаны в `requirements.txt`:

```
Flask==2.3.3
Flask-Login==0.6.3
Werkzeug==2.3.7
openpyxl==3.1.2
gunicorn==21.2.0
```

### 3. Создание файла wsgi.py

```python
from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    app.run()
```

## Подготовка Ubuntu сервера

### 1. Подключение к серверу

```bash
ssh username@77.240.39.36
```

### 2. Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Установка необходимых пакетов

```bash
# Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Git
sudo apt install git -y

# Nginx (веб-сервер)
sudo apt install nginx -y

# Supervisor (для управления процессами)
sudo apt install supervisor -y

# Дополнительные пакеты
sudo apt install build-essential python3-dev -y
```

## Деплой проекта

### 1. Клонирование репозитория

```bash
# Переходим в домашнюю директорию
cd /home/username

# Или создаем директорию для проектов
sudo mkdir -p /var/www
sudo chown username:username /var/www
cd /var/www

# Клонируем репозиторий
git clone https://github.com/yourusername/supplier_management_system.git
cd supplier_management_system
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

```bash
# Создаем файл с переменными окружения
nano .env
```

Содержимое файла `.env`:

```
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-very-secret-key-here-change-this
DATABASE_URL=sqlite:///app.db
```

### 5. Инициализация базы данных

```bash
python init_db.py
```

### 6. Тестирование запуска

```bash
# Тестовый запуск
python run.py

# Или с Gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

## Настройка Nginx

### 1. Создание конфигурации Nginx

```bash
sudo nano /etc/nginx/sites-available/supplier_management
```

Содержимое файла:

```nginx
server {
    listen 80;
    server_name 77.240.39.36;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/supplier_management_system/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 16M;
}
```

### 2. Активация конфигурации

```bash
# Создаем символическую ссылку
sudo ln -s /etc/nginx/sites-available/supplier_management /etc/nginx/sites-enabled/

# Удаляем дефолтную конфигурацию
sudo rm /etc/nginx/sites-enabled/default

# Тестируем конфигурацию
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Настройка Supervisor

### 1. Создание конфигурации Supervisor

```bash
sudo nano /etc/supervisor/conf.d/supplier_management.conf
```

Содержимое файла:

```ini
[program:supplier_management]
command=/var/www/supplier_management_system/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app
directory=/var/www/supplier_management_system
user=username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supplier_management.log
environment=PATH="/var/www/supplier_management_system/venv/bin"
```

### 2. Запуск и управление через Supervisor

```bash
# Перечитываем конфигурацию
sudo supervisorctl reread
sudo supervisorctl update

# Запускаем приложение
sudo supervisorctl start supplier_management

# Проверяем статус
sudo supervisorctl status

# Другие команды:
# sudo supervisorctl stop supplier_management
# sudo supervisorctl restart supplier_management
```

## Настройка брандмауэра

```bash
# Разрешаем HTTP трафик
sudo ufw allow 80

# Разрешаем HTTPS (если планируете SSL)
sudo ufw allow 443

# Разрешаем SSH
sudo ufw allow 22

# Включаем брандмауэр
sudo ufw enable

# Проверяем статус
sudo ufw status
```

## Обновление проекта

### 1. Скрипт для обновления

Создайте файл `deploy.sh`:

```bash
#!/bin/bash

echo "Updating supplier management system..."

# Переходим в директорию проекта
cd /var/www/supplier_management_system

# Получаем последние изменения
git pull origin main

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем зависимости
pip install -r requirements.txt

# Перезапускаем приложение
sudo supervisorctl restart supplier_management

echo "Deploy completed!"
```

Сделайте скрипт исполняемым:

```bash
chmod +x deploy.sh
```

### 2. Использование скрипта

```bash
./deploy.sh
```

## SSL сертификат (опционально)

### Установка Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата (замените на ваш домен или IP)
sudo certbot --nginx -d YOUR_SERVER_IP
```

## Мониторинг и логи

### Просмотр логов

```bash
# Логи приложения
sudo tail -f /var/log/supplier_management.log

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Логи Supervisor
sudo tail -f /var/log/supervisor/supervisord.log
```

### Проверка статуса сервисов

```bash
# Статус Nginx
sudo systemctl status nginx

# Статус Supervisor
sudo systemctl status supervisor

# Статус приложения через Supervisor
sudo supervisorctl status
```

## Резервное копирование

### Создание бэкапа базы данных

```bash
# Создание директории для бэкапов
mkdir -p /var/backups/supplier_management

# Скрипт бэкапа
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /var/www/supplier_management_system/app.db /var/backups/supplier_management/app_${DATE}.db
```

## Проверка деплоя

1. Откройте браузер и перейдите по адресу: `http://77.240.39.36`
2. Проверьте, что сайт загружается корректно
3. Протестируйте основной функционал
4. Проверьте загрузку статических файлов

## Устранение проблем

### Проверка портов

```bash
# Проверяем, какие порты слушает система
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :5000
```

### Проверка процессов

```bash
# Проверяем процессы Gunicorn
ps aux | grep gunicorn

# Проверяем процессы Python
ps aux | grep python
```

### Перезапуск всех сервисов

```bash
sudo systemctl restart nginx
sudo supervisorctl restart supplier_management
```

---

**Примечание:** IP-адрес сервера `77.240.39.36` уже настроен. Замените `username` на ваше имя пользователя на сервере.