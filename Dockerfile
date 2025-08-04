FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar scripts y archivos necesarios
COPY scripts/ ./scripts/
COPY data/ ./data/

# Crear directorios necesarios
RUN mkdir -p faqs_markdown pages posts

# Script de entrada
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Exponer puerto (opcional, para futuras APIs)
EXPOSE 8000

# Comando por defecto
CMD ["python", "railway_config.py"] 