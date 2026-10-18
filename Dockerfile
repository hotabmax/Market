# ============================================
# Этап 1: Сборка зависимостей
# ============================================
FROM python:3.12-slim AS builder

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости
WORKDIR /app

# Копируем только requirements для кэширования
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Этап 2: Production образ
# ============================================
FROM python:3.12-slim AS production

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создаём пользователя для безопасности
RUN groupadd --system django && \
    useradd --system --gid django --home-dir /home/django django

# Копируем зависимости из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Создаём рабочую директорию
WORKDIR /app

# Копируем приложение
COPY --chown=django:django . .

# Создаём директории для статики и медиа
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R django:django /app

# Переключаемся на небезопасного пользователя
USER django

# Открываем порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Запускаем entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Запускаем Gunicorn
CMD ["gunicorn", "market.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
