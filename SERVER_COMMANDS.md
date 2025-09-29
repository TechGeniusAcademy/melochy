# Готовые команды для сервера 77.240.39.36

## Подключение к серверу
```bash
ssh username@77.240.39.36
```

## Команды для исправления проблемы с Supervisor

```bash
# 1. Перейти в директорию проекта
cd /var/www/melochy

# 2. Получить последние изменения
git pull origin main

# 3. Удалить старые конфигурации Supervisor
sudo rm -f /etc/supervisor/conf.d/supplier_management.conf

# 4. Скопировать правильную конфигурацию
sudo cp supervisor.conf /etc/supervisor/conf.d/melochy.conf

# 5. Скопировать конфигурацию Nginx
sudo cp nginx.conf /etc/nginx/sites-available/melochy

# 6. Перезапустить Supervisor
sudo systemctl restart supervisor

# 7. Запустить приложение
sudo supervisorctl start melochy

# 8. Проверить статус
sudo supervisorctl status

# 9. Перезапустить Nginx
sudo systemctl restart nginx

# 10. Проверить права доступа к статическим файлам
sudo chown -R www-data:www-data /var/www/melochy/app/static
sudo chmod -R 755 /var/www/melochy/app/static

# 11. Тест конфигурации Nginx
sudo nginx -t
```

## Устранение проблем с CSS/статикой

```bash
# 1. Получить обновления из Git
cd /var/www/melochy
git pull origin main

# 2. Обновить конфигурацию Nginx (правильный способ)
sudo cp nginx.conf /etc/nginx/sites-available/melochy

# АЛЬТЕРНАТИВНЫЙ способ - редактирование напрямую:
# sudo nano /etc/nginx/sites-available/melochy

# 3. Проверить права доступа
sudo chown -R www-data:www-data /var/www/melochy/app/static
sudo chmod -R 755 /var/www/melochy/app/static

# 4. Проверить существование файлов
ls -la /var/www/melochy/app/static/css/
ls -la /var/www/melochy/app/static/js/

# 5. Тест конфигурации и перезапуск
sudo nginx -t
sudo systemctl restart nginx

# 6. Проверить логи статики
sudo tail -f /var/log/nginx/static_access.log
sudo tail -f /var/log/nginx/melochy_error.log
```

## Если нужно редактировать nginx.conf напрямую на сервере

```bash
# Используйте sudo для редактирования системных файлов
sudo nano /etc/nginx/sites-available/melochy

# Или используйте vim
sudo vim /etc/nginx/sites-available/melochy

# После редактирования обязательно проверьте синтаксис
sudo nginx -t

# И перезапустите nginx
sudo systemctl restart nginx
```

## Проверка результата

Откройте в браузере: http://77.240.39.36

## Полезные команды для мониторинга

```bash
# Логи приложения
sudo tail -f /var/log/supervisor/melochy.log

# Логи Nginx
sudo tail -f /var/log/nginx/melochy_error.log

# Статус всех сервисов
sudo supervisorctl status
sudo systemctl status nginx

# Перезапуск приложения
sudo supervisorctl restart melochy
```