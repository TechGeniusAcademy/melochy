# Быстрый деплой - Краткая инструкция

## 1. Подготовка сервера (одноразово)

```bash
# Подключение к серверу
ssh username@77.240.39.36

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
git clone https://github.com/yourusername/melochy.git
cd melochy

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
sudo cp nginx.conf /etc/nginx/sites-available/melochy

# Редактирование конфигурации (IP уже настроен: 77.240.39.36)
sudo nano /etc/nginx/sites-available/melochy

# Активация сайта
sudo ln -s /etc/nginx/sites-available/melochy /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Тест и перезапуск Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 4. Настройка Supervisor

```bash
# Копирование конфигурации
sudo cp supervisor.conf /etc/supervisor/conf.d/melochy.conf

# Проверка, что файл создался
ls -la /etc/supervisor/conf.d/melochy.conf

# Проверка содержимого файла
sudo cat /etc/supervisor/conf.d/melochy.conf

# ВАЖНО: Удалить старые конфигурации если есть
sudo rm -f /etc/supervisor/conf.d/supplier_management.conf

# Обновление Supervisor (важно делать в правильном порядке)
sudo supervisorctl reread
sudo supervisorctl update

# Проверка доступных программ
sudo supervisorctl avail

# Запуск приложения
sudo supervisorctl start melochy

# Проверка статуса
sudo supervisorctl status

# Если есть ошибки, проверить логи
sudo tail -f /var/log/supervisor/melochy.log
```

## 5. Настройка прав доступа

```bash
sudo chown -R www-data:www-data /var/www/melochy
sudo chmod -R 755 /var/www/melochy
sudo chmod -R 775 /var/www/melochy/app/static/uploads
```

## 6. Настройка брандмауэра

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS (если нужно)
sudo ufw enable
```

## 7. Проверка работы

Откройте в браузере: `http://77.240.39.36`

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
sudo tail -f /var/log/supervisor/melochy.log
sudo tail -f /var/log/nginx/melochy_error.log
sudo tail -f /var/log/nginx/static_access.log

# Управление приложением
sudo supervisorctl restart melochy
sudo supervisorctl stop melochy
sudo supervisorctl start melochy

# Перезапуск сервисов
sudo systemctl restart nginx
sudo systemctl restart supervisor

# Проверка статических файлов
ls -la /var/www/melochy/app/static/css/
curl -I http://77.240.39.36/static/css/style.css
```

## Устранение проблем

### Проблема: "ERROR (no such process)" при запуске

```bash
# 1. Удалить старые конфигурации
sudo rm -f /etc/supervisor/conf.d/supplier_management.conf

# 2. Скопировать новую конфигурацию
sudo cp supervisor.conf /etc/supervisor/conf.d/melochy.conf

# 3. Перезапустить Supervisor полностью
sudo systemctl restart supervisor

# 4. Проверить статус
sudo supervisorctl status

# 5. Запустить приложение
sudo supervisorctl start melochy
```

### Проблема: "ERROR (no such file)" 

```bash
# Проверить существование конфигурационного файла
ls -la /etc/supervisor/conf.d/

# Если файла нет, скопировать заново
sudo cp supervisor.conf /etc/supervisor/conf.d/melochy.conf

# Перечитать конфигурацию
sudo supervisorctl reread
sudo supervisorctl update
```

### Проблема с правами доступа

```bash
# Проверить права на директорию
ls -la /var/www/melochy

# Исправить права
sudo chown -R www-data:www-data /var/www/melochy
sudo chmod -R 755 /var/www/melochy
```

### Проблема: CSS/JS файлы не загружаются

```bash
# 1. Проверить существование статических файлов
ls -la /var/www/melochy/app/static/css/
ls -la /var/www/melochy/app/static/js/

# 2. Обновить конфигурацию Nginx
git pull origin main
sudo cp nginx.conf /etc/nginx/sites-available/melochy

# 3. Исправить права на статические файлы
sudo chown -R www-data:www-data /var/www/melochy/app/static
sudo chmod -R 755 /var/www/melochy/app/static

# 4. Перезапустить Nginx
sudo nginx -t
sudo systemctl restart nginx

# 5. Проверить доступность CSS файла
curl -I http://77.240.39.36/static/css/style.css

# 6. Проверить логи ошибок
sudo tail -f /var/log/nginx/melochy_error.log
```

---

**Готово!** IP адрес `77.240.39.36` уже настроен во всех конфигурационных файлах.