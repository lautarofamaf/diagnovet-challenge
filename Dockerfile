# 1. Usamos una imagen ligera de Python 3.11
FROM python:3.11-slim

# 2. Evitamos archivos .pyc y logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo
WORKDIR /app

# 4. INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. INSTALACIÓN DE LIBRERÍAS PYTHON 
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el resto del código
COPY . .

# 7. Comando de arranque
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
