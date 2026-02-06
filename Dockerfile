# 1. Usamos una imagen ligera de Python 3.11
FROM python:3.11-slim

# 2. Evitamos que Python genere archivos .pyc y bufferee la salida (logs en tiempo real)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo en el contenedor
WORKDIR /app

# 4. Copiamos los requisitos e instalamos dependencias
# Instalar dependencias del sistema necesarias para PyMuPDF/OpenCV si hiciera falta (glib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto del código
COPY . .

# 6. El comando de arranque
# Render nos pasa el puerto en la variable de entorno PORT. Usamos 8080 por defecto.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
