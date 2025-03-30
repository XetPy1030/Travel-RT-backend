FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libffi-dev \
        libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Установка и настройка Poetry
ENV POETRY_VERSION=2.1.1 \
    PATH="${PATH}:/root/.local/bin"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10

# Установка зависимостей проекта
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

# Копирование исходного кода
COPY . .
