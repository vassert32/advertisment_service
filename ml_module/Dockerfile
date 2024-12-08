FROM python:3.9-slim

WORKDIR /app

# Установка обновленной версии pip
RUN pip install --upgrade pip

# Установка зависимостей
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY ./app /app/app

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
