#!/bin/bash

# Скрипт автоматического деплоя для системы управления поставщиками
# Использование: ./deploy.sh

echo "🚀 Начинаем деплой системы управления поставщиками..."

# Определяем директорию проекта
PROJECT_DIR="/var/www/melochy"
BACKUP_DIR="/var/backups/melochy"

# Функция для вывода сообщений
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Функция для проверки успешности команды
check_status() {
    if [ $? -eq 0 ]; then
        log "✅ $1 - успешно"
    else
        log "❌ $1 - ошибка"
        exit 1
    fi
}

# Создаем бэкап базы данных
log "Создание бэкапа базы данных..."
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
if [ -f "$PROJECT_DIR/app.db" ]; then
    cp $PROJECT_DIR/app.db $BACKUP_DIR/app_backup_${DATE}.db
    check_status "Бэкап базы данных"
fi

# Переходим в директорию проекта
cd $PROJECT_DIR
check_status "Переход в директорию проекта"

# Получаем последние изменения из Git
log "Получение последних изменений из Git..."
git fetch origin
git pull origin main
check_status "Обновление кода из Git"

# Активируем виртуальное окружение
log "Активация виртуального окружения..."
source venv/bin/activate
check_status "Активация виртуального окружения"

# Обновляем зависимости
log "Обновление Python зависимостей..."
pip install -r requirements.txt --upgrade
check_status "Установка зависимостей"

# Применяем миграции базы данных (если есть)
if [ -f "init_db.py" ]; then
    log "Применение изменений базы данных..."
    python init_db.py
    check_status "Обновление базы данных"
fi

# Собираем статические файлы (если нужно)
log "Проверка статических файлов..."
if [ ! -d "app/static" ]; then
    mkdir -p app/static
fi

# Устанавливаем правильные права доступа
log "Установка прав доступа..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod -R 775 $PROJECT_DIR/app/static/uploads
check_status "Установка прав доступа"

# Перезапускаем приложение через Supervisor
log "Перезапуск приложения..."
sudo supervisorctl restart melochy
check_status "Перезапуск приложения"

# Перезагружаем конфигурацию Nginx
log "Перезагрузка Nginx..."
sudo nginx -t && sudo systemctl reload nginx
check_status "Перезагрузка Nginx"

# Проверяем статус сервисов
log "Проверка статуса сервисов..."
echo "Статус приложения:"
sudo supervisorctl status melochy

echo "Статус Nginx:"
sudo systemctl status nginx --no-pager -l

# Проверяем доступность приложения
log "Проверка доступности приложения..."
sleep 3
if curl -f -s http://localhost > /dev/null; then
    log "✅ Приложение доступно"
else
    log "⚠️  Приложение может быть недоступно, проверьте логи"
fi

log "🎉 Деплой завершен успешно!"
echo ""
echo "📋 Полезные команды для мониторинга:"
echo "   Логи приложения: sudo tail -f /var/log/supervisor/melochy.log"
echo "   Логи Nginx: sudo tail -f /var/log/nginx/melochy_error.log"
echo "   Статус приложения: sudo supervisorctl status"
echo "   Перезапуск приложения: sudo supervisorctl restart melochy"