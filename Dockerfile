FROM python:3.9-slim

# Buenas prácticas: No generar archivos .pyc y mostrar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Variables de entorno
ENV FLASK_ENV=production
ENV PORT=8000

EXPOSE 8000

# IMPORTANTE: Apuntamos a la función create_app() de tu app.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]