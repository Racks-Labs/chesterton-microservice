#!/bin/bash

echo "🚀 Ejecutando Microservicio Chesterton..."
echo ""

# Verificar que el archivo .env existe
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env"
    echo "💡 Ejecuta ./setup.sh primero para configurar el entorno"
    exit 1
fi

# Verificar que Docker está ejecutándose
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está ejecutándose"
    echo "💡 Inicia Docker Desktop o el servicio de Docker"
    exit 1
fi

echo "✅ Docker está ejecutándose"
echo ""

# Construir y ejecutar el microservicio
echo "🔨 Construyendo imagen Docker..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Imagen construida exitosamente"
    echo ""
    echo "🚀 Iniciando microservicio..."
    echo "📋 Los logs aparecerán a continuación:"
    echo "   (Presiona Ctrl+C para detener)"
    echo ""
    
    # Ejecutar el microservicio
    docker-compose up
else
    echo "❌ Error al construir la imagen Docker"
    exit 1
fi 