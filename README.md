# 📚 Library — Library API

REST API для управления библиотекой: книги, авторы, пользователи и выдачи. 
Поддерживает регистрацию, JWT-аутентификацию и автогенерируемую документацию OpenAPI.

---

## 🚀 Стек

- Python 3.12
- Django 5 + Django REST Framework
- PostgreSQL
- SimpleJWT
- drf-spectacular
- Docker, Docker Compose
- pytest

---

## 🧩 Структура

```
<repo_root>/
├─ config/                 # Настройки Django (settings.py, urls.py, wsgi/asgi.py)
├─ users/                  # Пользователи и аутентификация
├─ library/                # Библиотека
├─ tests/                  # Тесты
├─ Dockerfile
├─ docker-compose.yml
├─ pyproject.toml
├─ .env.template
└─ README.md
```

---

## ⚙️ Локальный запуск (Poetry)

```bash
# Клонировать
git clone https://github.com/<username>/<repo>.git
cd <repo>

# Установить зависимости
poetry install

# Настроить окружение
cp .env.template .env
```

Пример `.env`:
```dotenv
SECRET_KEY=secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=library
POSTGRES_USER=library
POSTGRES_PASSWORD=library
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=Admin123!
LOAN_DEFAULT_DAYS=days_number
ALLOW_SELF_ISSUE=1IfTrue
```

Применить миграции:
```bash
poetry run python manage.py migrate
```

Запуск:
```bash
poetry run python manage.py runserver
# http://127.0.0.1:8000
```

---

## 🐳 Запуск в Docker

```bash
docker compose up -d --build
# проверить логи веб-сервиса:
docker compose logs -f web
# применить миграции:
docker compose exec web python manage.py migrate
```

Сервисы в `docker-compose`:
- web
- db

По умолчанию приложение доступно на `http://localhost:8000`.

---

## 🔑 Аутентификация

## ВАЖНО! При запуске через Docker Compose автоматически создается супер-юзер с заданными кредитами из .env
JWT (SimpleJWT):
- `POST /api/auth/token` — получить access/refresh
- `POST /api/auth/refresh` — обновить access
- `POST /api/auth/register` — регистрация (если реализована)

Пример запроса на получение токена:
```http
POST /api/auth/token
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "S3curePass!"
}
```

Использование Access токена:
```
Authorization: Bearer <access_token>
```

---

### Выдача книг (Loans)
- `POST /api/loans/issue/` — выдать книгу пользователю
- `POST /api/loans/return/` — вернуть книгу
- Контроль доступности: поле `copies_available` у книги
- Срок возврата: из `LOAN_DEFAULT_DAYS`

---

## 🔎 Поиск, фильтры и сортировка

- Поиск: `?search=<строка>` (название книги, автор и др.)
- Фильтры: `?genre=...&author=...&year=...`
- Сортировка: `?ordering=year,-title`

Пагинация:
- Параметры: `?page=1&page_size=20`

---

## 📘 OpenAPI документация

- `/api/schema/        — JSON схема`
- `/api/schema.yaml    — YAML схема`
- `/api/docs/          — Swagger UI`
- `/api/redoc/         — ReDoc UI`

Пример добавления в `urls.py`:
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

---

## ✅ Качество кода и тесты

Линтеры/форматтеры:
- black/isort/flake8

Тесты:
```bash
pytest
```

Покрытие:
```bash
pytest --cov
```

---

## 📝 Бизнес-правила (пример)

- Нельзя выдать книгу, если `copies_available == 0`.
- Пользователь видит свои выдачи, администратор — все.
- Возврат книги увеличивает `copies_available`.
- Статусы: `ISSUED`, `RETURNED`, `OVERDUE` (если применимо).

---

## 🧰 Полезные команды

```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Собрать статические файлы (если нужно)
python manage.py collectstatic --noinput
```

---

## 📄 Лицензия

Учебный проект.
