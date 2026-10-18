#!/bin/bash
set -e

# ============================================
# Docker Entrypoint for Django Market
# ============================================

echo "🚀 Starting Market application..."

# Проверяем переменные окружения
if [ -z "$DJANGO_SECRET_KEY" ]; then
    echo "❌ ERROR: DJANGO_SECRET_KEY is not set!"
    exit 1
fi

# Ждём готовности базы данных
echo "⏳ Waiting for database to be ready..."
until python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'market'),
        user=os.environ.get('DB_USER', 'market_user'),
        password=os.environ.get('DB_PASSWORD', 'market_password'),
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432')
    )
    conn.close()
    exit(0)
except:
    exit(1)
"; do
    echo "   Database is unavailable - sleeping"
    sleep 2
done
echo "✅ Database is ready!"

# Применяем миграции
echo "📦 Applying database migrations..."
python manage.py migrate --noinput

# Собираем статику
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Создаём директории если не существуют
mkdir -p /app/staticfiles /app/media

# Запускаем collectstatic для медиа (если нужно)
echo "✅ Setup complete!"

# Передаём управление CMD
exec "$@"
