# Путешествуем по Республике Татарстан 🏰

Веб-приложение для планирования путешествий по Республике Татарстан, построенное на Django.

## Возможности

- Просмотр достопримечательностей и туристических мест
- Планирование маршрутов
- Отзывы и рейтинги мест
- Личный кабинет путешественника

## Технологии

- Python 3.12+
- Django 5
- PostgreSQL
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

