# Быстрый деплой - Краткая инструкция

## 1. Подготовка сервера (одноразово)

```bash
# Подключение к серверу
ssh username@YOUR_SERVER_IP

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install python3 python3-pip python3-venv git nginx supervisor -y

# Создание директории для проекта
sudo mkdir -p /var/www
sudo chown $USER:$USER /var/www
```

## 2. Клонирование и настройка проекта

```bash
# Клонирование репозитория
cd /var/www
git clone https://github.com/yourusername/supplier_management_system.git
cd supplier_management_system

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Копирование и настройка переменных окружения
cp .env.example .env
nano .env  # Измените SECRET_KEY и другие настройки

# Инициализация базы данных
python init_db.py

# Тест запуска
python wsgi.py
```

## 3. Настройка Nginx

```bash
# Копирование конфигурации
sudo cp nginx.conf /etc/nginx/sites-available/supplier_management

# Редактирование конфигурации (замените YOUR_SERVER_IP)
sudo nano /etc/nginx/sites-available/supplier_management

# Активация сайта
sudo ln -s /etc/nginx/sites-available/supplier_management /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Тест и перезапуск Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 4. Настройка Supervisor

```bash
# Копирование конфигурации
sudo cp supervisor.conf /etc/supervisor/conf.d/supplier_management.conf

# Обновление Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start supplier_management

# Проверка статуса
sudo supervisorctl status
```

## 5. Настройка прав доступа

```bash
sudo chown -R www-data:www-data /var/www/supplier_management_system
sudo chmod -R 755 /var/www/supplier_management_system
sudo chmod -R 775 /var/www/supplier_management_system/app/static/uploads
```

## 6. Настройка брандмауэра

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS (если нужно)
sudo ufw enable
```

## 7. Проверка работы

Откройте в браузере: `http://YOUR_SERVER_IP`

## 8. Обновление проекта (в будущем)

```bash
# Сделайте deploy.sh исполняемым (одноразово)
chmod +x deploy.sh

# Для обновления просто запустите
./deploy.sh
```

## Полезные команды

```bash
# Проверка логов
sudo tail -f /var/log/supervisor/supplier_management.log
sudo tail -f /var/log/nginx/supplier_management_error.log

# Управление приложением
sudo supervisorctl restart supplier_management
sudo supervisorctl stop supplier_management
sudo supervisorctl start supplier_management

# Перезапуск сервисов
sudo systemctl restart nginx
sudo systemctl restart supervisor
```

---

**Важно:** Не забудьте заменить `YOUR_SERVER_IP` на реальный IP адрес вашего сервера во всех конфигурационных файлах!