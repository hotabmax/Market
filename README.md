# 🛒 ФрешМаркет — Интернет-магазин продуктов питания

Интернет-магазин продуктов питания на **Django 6.1** с полным функционалом: каталог, корзина, оформление заказа, отслеживание и отмена заказов.

[![Django](https://img.shields.io/badge/Django-6.1-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-55/55-passing-brightgreen)](shop/tests.py)

---

## ✨ Возможности

### Для покупателей
- 📦 **Каталог** — фильтрация по категориям, поиск, сортировка, фильтр по цене
- 🛒 **Корзина** — добавление, удаление, изменение количества товаров
- 💳 **Оформление заказа** — форма с валидацией, расчёт итоговой суммы
- 📋 **Отслеживание заказов** — поиск по email, просмотр статуса и деталей
- ❌ **Отмена заказа** — отмена только новых заказов с возвратом на склад
- 📱 **Адаптивный дизайн** — Bootstrap 5, работает на всех устройствах

### Для администраторов
- 📊 **Админ-панель** — управление категориями, товарами, заказами
- 📈 **Статистика заказов** — статусы, суммы, детали
- 🏷️ **Управление скидками** — старая/новая цена, процент скидки

### Безопасность
- 🔒 **IDOR protection** — проверка email для доступа к заказам
- 🛡️ **Защита корзины** — цена берётся из БД, не из сессии
- ⏱️ **Rate limiting** — ограничение частоты запросов
- 🔐 **Security headers** — HSTS, CSP, X-Frame-Options
- 📝 **Логирование** — аудит создания и отмены заказов

---

## 📸 Скриншоты

| Главная | Каталог | Корзина |
|---------|---------|---------|
| 🏠 Главная страница с категориями и товарами | 🔍 Каталог с фильтрами | 🛒 Корзина с итогами |

| Оформление | Подтверждение | Мои заказы |
|-----------|--------------|------------|
| 📝 Форма оформления заказа | ✅ Подтверждение заказа | 📋 Список заказов |

---

## 🛠 Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Backend | Django 6.1, Python 3.12 |
| Frontend | Bootstrap 5.3, Font Awesome 6 |
| Database | PostgreSQL (prod) / SQLite (dev) |
| Server | Gunicorn (prod) / Django dev server |
| Reverse Proxy | Nginx (prod) |
| Container | Docker, Docker Compose |

---

## 🚀 Быстрый старт

### Требования

- Python 3.12+
- pip и venv
- Или Docker + Docker Compose

### Вариант 1: Локальная установка

```bash
# 1. Клонировать репозиторий
git clone <your-repo-url>
cd Market

# 2. Создать виртуальное окружение
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Создать суперпользователя
python manage.py createsuperuser

# 6. Заполнить базу данными
python populate_db.py

# 7. Запустить сервер
python manage.py runserver
```

Открыть: http://127.0.0.1:8000/
Админ-панель: http://127.0.0.1:8000/admin/

### Вариант 2: Docker (рекомендуется для production)

```bash
# 1. Настроить окружение
cp .env.production.example .env
# Отредактировать .env: DJANGO_SECRET_KEY, DB_PASSWORD

# 2. Собрать и запустить
docker compose build
docker compose up -d

# 3. Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# 4. Заполнить данными
docker compose exec web python populate_db.py
```

Открыть: http://localhost/

---

## 📁 Структура проекта

```
Market/
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Services: web, db, nginx
├── docker-entrypoint.sh        # Container startup script
├── .dockerignore               # Files to exclude from build
├── requirements.txt            # Python dependencies
├── populate_db.py              # Script to populate sample data
│
├── market/                     # Django project settings
│   ├── settings.py             # Settings (env-based)
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
│
├── shop/                       # Main application
│   ├── models.py               # Category, Product, Order, OrderItem
│   ├── views.py                # All views with security
│   ├── forms.py                # OrderCreateForm, OrderEmailForm
│   ├── middleware.py           # Rate limiting, cart protection
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Admin configuration
│   ├── tests.py                # 55 unit/integration tests
│   ├── templates/shop/         # HTML templates
│   │   ├── base.html           # Base template with nav
│   │   ├── home.html           # Homepage
│   │   ├── catalog.html        # Product catalog
│   │   ├── product_detail.html # Product page
│   │   ├── cart.html           # Shopping cart
│   │   ├── checkout.html       # Order form
│   │   ├── order_detail.html   # Order confirmation
│   │   └── orders_list.html    # Orders list by email
│   └── fixtures/               # Data fixtures
│
├── nginx/                      # Nginx configuration
│   ├── conf.d/default.conf     # Server configuration
│   └── ssl/                    # SSL certificates
│
├── static/                     # Static files (CSS, JS)
│   ├── css/style.css
│   └── js/main.js
│
├── media/                      # Uploaded images
├── .env.example                # Environment variables template
├── .env.production.example     # Production env template
├── DEPLOYMENT.md               # Deployment guide
└── SECURITY_AUDIT.md           # Security audit report
```

---

## 🧪 Тестирование

```bash
# Запустить все тесты
python manage.py test shop

# С подробным выводом
python manage.py test shop --verbosity=2

# Только конкретный тест
python manage.py test shop.ViewTests.test_home_page_status_code
```

**Результат:** 55 тестов, 100% пройдены ✅

| Категория | Кол-во | Описание |
|-----------|--------|----------|
| Model tests | 17 | Category, Product, CartItem, Order, OrderItem |
| View tests | 24 | Home, catalog, product, cart, checkout, orders |
| Form tests | 3 | OrderCreateForm, ProductSearchForm |
| Security tests | 11 | IDOR, rate limiting, price protection |

---

## 🔧 Настройка

### Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django | `change-me` |
| `DJANGO_DEBUG` | Режим отладки | `True` |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `DB_ENGINE` | Движок БД | `sqlite3` |
| `DB_NAME` | Имя базы данных | `db.sqlite3` |
| `DB_USER` | Пользователь БД | (пусто) |
| `DB_PASSWORD` | Пароль БД | (пусто) |
| `DB_HOST` | Хост БД | (пусто) |
| `DB_PORT` | Порт БД | (пусто) |

### Production настройки

Для production используйте `.env.production.example`:

```bash
DJANGO_SECRET_KEY=<generated-64-char-key>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=market
DB_USER=market_user
DB_PASSWORD=<strong-password-32-chars>
```

---

## 📊 Модели данных

### Category
| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField | Название категории |
| slug | SlugField | URL-идентификатор |
| image | ImageField | Изображение категории |
| description | TextField | Описание |
| active | BooleanField | Активность |

### Product
| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField | Название товара |
| slug | SlugField | URL-идентификатор |
| category | ForeignKey | Категория |
| price | DecimalField | Цена |
| old_price | DecimalField | Старая цена (скидка) |
| weight | CharField | Вес/Объём |
| stock | PositiveIntegerField | Остаток на складе |
| available | BooleanField | Доступность |
| featured | BooleanField | Рекомендуемый |

### Order
| Поле | Тип | Описание |
|------|-----|----------|
| first_name | CharField | Имя |
| last_name | CharField | Фамилия |
| email | EmailField | Email (для отслеживания) |
| phone | CharField | Телефон |
| address | TextField | Адрес доставки |
| status | CharField | new → processing → shipped → delivered |
| total_price | DecimalField | Итого |

---

## 🌐 API endpoints

| Method | URL | Описание |
|--------|-----|----------|
| GET | `/` | Главная страница |
| GET | `/catalog/` | Каталог товаров |
| GET | `/catalog/<slug>/` | Страница товара |
| GET | `/cart/` | Корзина |
| POST | `/cart/add/<slug>/` | Добавить в корзину |
| POST | `/cart/remove/<id>/` | Удалить из корзины |
| POST | `/cart/update/` | Обновить корзину |
| GET | `/checkout/` | Оформление заказа |
| POST | `/checkout/` | Подтвердить заказ |
| GET | `/orders/` | Список заказов |
| GET | `/order/<id>/` | Детали заказа |
| POST | `/order/<id>/cancel/` | Отменить заказ |
| GET | `/admin/` | Админ-панель |

---

## 📦 Деплой

### Docker

```bash
# Собрать образы
docker compose build

# Запустить
docker compose up -d

# Проверить
docker compose ps
docker compose logs -f web

# Остановить
docker compose down

# С пересозданием
docker compose up -d --build
```

### Production (без Docker)

```bash
# Установить зависимости
pip install -r requirements.txt

# Собрать статику
python manage.py collectstatic --noinput

# Применить миграции
python manage.py migrate

# Запустить Gunicorn
gunicorn market.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

📖 Полная документация: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🔒 Безопасность

📖 Полный аудит: [SECURITY_AUDIT.md](SECURITY_AUDIT.md)

### Реализованная защита
- ✅ IDOR protection — проверка email для доступа к заказам
- ✅ Price protection — цена берётся из БД, не из сессии
- ✅ Rate limiting — ограничение частоты запросов
- ✅ CSRF protection — встроен в Django
- ✅ XSS protection — escape в шаблонах, CSP заголовки
- ✅ Clickjacking protection — X-Frame-Options: DENY
- ✅ HSTS — строгая транспортная безопасность
- ✅ Secure cookies — HttpOnly, Secure, SameSite
- ✅ Logging — аудит критических действий

---

## 📝 Лицензия

MIT

---

## 👨‍💻 Автор

Интернет-магазин продуктов питания «ФрешМаркет»
Built with ❤️ using Django 6.1
