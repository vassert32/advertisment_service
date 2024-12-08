FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей и netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY ./app /app/app

# Копирование скрипта wait-for-it.sh
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Запуск приложения с ожиданием PostgreSQL
CMD ["./wait-for-it.sh", "postgres", "5432", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
