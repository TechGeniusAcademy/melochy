# Исправление проблемы с CSS

## Проблема
CSS файлы не загружаются на сайте http://77.240.39.36

## Решение

### Вариант 1: Обновить через Git (Рекомендуется)

```bash
# 1. Перейти в директорию проекта
cd /var/www/melochy

# 2. Получить обновления из Git
git pull origin main

# 3. Скопировать обновленную конфигурацию Nginx
sudo cp nginx.conf /etc/nginx/sites-available/melochy

# 4. Проверить конфигурацию
sudo nginx -t

# 5. Перезапустить Nginx
sudo systemctl restart nginx
```

### Вариант 2: Редактировать конфигурацию напрямую

```bash
# 1. Открыть конфигурацию для редактирования
sudo nano /etc/nginx/sites-available/melochy

# 2. Найти секцию location /static и заменить на:
```

Добавьте в файл `/etc/nginx/sites-available/melochy`:

```nginx
    # Статические файлы (CSS, JS, изображения)
    location /static/ {
        alias /var/www/melochy/app/static/;
        expires 30d;
        add_header Cache-Control "public";
        
        # Обработка MIME типов
        location ~* \.(css)$ {
            add_header Content-Type text/css;
            expires 30d;
        }
        
        location ~* \.(js)$ {
            add_header Content-Type application/javascript;
            expires 30d;
        }
        
        location ~* \.(png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Логирование для отладки
        access_log /var/log/nginx/static_access.log;
    }
```

### После любого из вариантов:

```bash
# Проверить права доступа
sudo chown -R www-data:www-data /var/www/melochy/app/static
sudo chmod -R 755 /var/www/melochy/app/static

# Проверить существование CSS файлов
ls -la /var/www/melochy/app/static/css/

# Тест доступности CSS
curl -I http://77.240.39.36/static/css/style.css

# Проверить логи ошибок
sudo tail -f /var/log/nginx/melochy_error.log
```

## Проверка результата

1. Откройте сайт: http://77.240.39.36
2. Нажмите F12 для открытия инструментов разработчика
3. Проверьте вкладку Network - CSS файлы должны загружаться с кодом 200
4. Проверьте вкладку Console на ошибки

## Дополнительная отладка

```bash
# Проверить процессы Nginx
sudo systemctl status nginx

# Проверить слушающие порты
sudo netstat -tulpn | grep :80

# Проверить логи доступа
sudo tail -f /var/log/nginx/melochy_access.log

# Перезапустить все сервисы
sudo systemctl restart nginx
sudo supervisorctl restart melochy
```