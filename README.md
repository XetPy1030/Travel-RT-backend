# Путешествуем по Республике Татарстан 🏰

Веб-приложение для планирования путешествий по Республике Татарстан, построенное на Django.

## Возможности

- Просмотр достопримечательностей и туристических мест (с тегами и фильтрацией)
- Планирование маршрутов
- **ИИ-генерация маршрутов** — по запросу пользователя (город/район, пожелания) строится маршрут с точками и описанием
- **ИИ-тегирование мест** — в админке можно подобрать теги для мест с помощью ИИ (OpenRouter)
- Отзывы и рейтинги мест
- Личный кабинет путешественника

## Технологии

- Python 3.11+
- Django 5
- PostgreSQL
- Celery + Redis (очередь задач для генерации маршрутов)
- OpenRouter (LLM для тегов и генерации маршрутов)
- Docker
- Poetry

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/XetPy1030/travel-rt.git
   cd travel-rt
   ```

2. Установите Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Установите зависимости:
   ```bash
   poetry install
   ```

4. Скопируйте файл .env-example в .env:
   ```bash
   cp .env-example .env
   ```
   И отредактируйте необходимые переменные окружения в .env файле

5. Примените миграции:
   ```bash
   poetry run python manage.py migrate
   ```

6. Загрузите начальные данные:
   ```bash
   poetry run python manage.py loaddata tatarstan_locations.json
   ```

7. Загрузите примеры данных:
   ```bash
   poetry run python manage.py loaddata example_data.json
   ```

8. Переименуйте папку example_media в media:
   ```bash
   mv example_media media
   ```

9. Запустите сервер разработки:
   ```bash
   poetry run python manage.py runserver
   ```

## Запуск через Docker Compose

В корне бэкенда (где лежит `docker-compose.yml`):

1. Создайте `.env` из `.env-example` и при необходимости отредактируйте переменные.
2. Запустите сервисы:
   ```bash
   docker compose up -d
   ```
   Поднимаются: **postgres** (порт 5432), **redis** (порт 6379), **app** (Django на порту 8000), **celery** (воркер для
   генерации маршрутов).
3. Первый запуск — примените миграции и при необходимости загрузите фикстуры:
   ```bash
   docker compose exec app python manage.py migrate
   docker compose exec app python manage.py loaddata initial_tags  # опционально, теги уже в миграции
   ```
4. Приложение доступно по адресу http://localhost:8000

Остановка: `docker compose down`. Данные PostgreSQL и Redis сохраняются в томах `travel-postgres` и `travel-redis`.

## ИИ: тегирование и генерация маршрутов

Для работы тегирования мест и генерации маршрутов нужен ключ OpenRouter. В `.env` задайте:

- `OPENROUTER_API_KEY` — ключ с [OpenRouter](https://openrouter.ai/)
- `OPENROUTER_MODEL` — модель (по умолчанию `meta-llama/llama-3.1-8b-instruct:free`)

**Генерация маршрутов** выполняется асинхронно через Celery. Дополнительно:

1. Установите и запустите **Redis** (например, `redis-server` или Docker).
2. В `.env` укажите `CELERY_BROKER_URL=redis://localhost:6379/0`.
3. В отдельном терминале запустите воркер Celery:
   ```bash
   celery -A travel worker -l info
   ```

После этого пользователи могут на фронте нажать «Сгенерировать маршрут», заполнить форму (текст + опционально
город/район) и получить маршрут по прямой ссылке. ИИ-маршруты не показываются в общем списке маршрутов (поле
`creation_method=ai_generated`).

## Логирование

Уровень логирования задаётся переменной `LOG_LEVEL` (значения: `DEBUG`, `INFO`, `WARNING`, `ERROR`). По умолчанию —
`INFO`. Вызовы LLM и ошибки ИИ пишутся в логгер `travel.ai`.

## Переменные окружения (.env)

| Переменная             | Описание                                                        |
|------------------------|-----------------------------------------------------------------|
| `POSTGRES_*`           | Подключение к PostgreSQL                                        |
| `PARSER_SERVICE_TOKEN` | Токен для парсера (если используется)                           |
| `OPENROUTER_API_KEY`   | Ключ API OpenRouter для ИИ                                      |
| `OPENROUTER_MODEL`     | Модель LLM (по умолчанию meta-llama/llama-3.1-8b-instruct:free) |
| `CELERY_BROKER_URL`    | URL брокера Celery (например redis://localhost:6379/0)          |
| `LOG_LEVEL`            | Уровень логирования: DEBUG, INFO, WARNING, ERROR                |

