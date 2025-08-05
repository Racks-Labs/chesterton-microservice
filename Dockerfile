FROM python:3.11-slim

# Instalar dependencias de compilación y de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y actualizar pip/setuptools/wheel
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY scripts/ ./scripts/
COPY data/ ./data/

# Crear directorios de salida
RUN mkdir -p faqs_markdown pages posts

# Script de entrada
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Exponer puerto (opcional)
EXPOSE 8000

# Comando por defecto
CMD ["python", "railway_config.py"]
