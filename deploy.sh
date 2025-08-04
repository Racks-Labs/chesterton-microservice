#!/bin/bash

# Script de despliegue para producción

set -e  # Salir en caso de error

echo "🚀 Desplegando Microservicio Chesterton en Producción..."
echo ""

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env"
    echo "💡 Configura las variables de entorno antes del despliegue"
    exit 1
fi

# Verificar variables críticas de producción
source .env

echo "🔍 Verificando configuración de producción..."

# Verificar variables críticas
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "TU_GOOGLE_API_KEY_AQUI" ]; then
    echo "❌ Error: GOOGLE_API_KEY no está configurada"
    exit 1
fi

if [ -z "$QDRANT_URL" ] || [ "$QDRANT_URL" = "https://tu-cluster.qdrant.io:6333" ]; then
    echo "❌ Error: QDRANT_URL no está configurada"
    exit 1
fi

if [ -z "$QDRANT_API_KEY" ] || [ "$QDRANT_API_KEY" = "tu_qdrant_api_key_aqui" ]; then
    echo "❌ Error: QDRANT_API_KEY no está configurada"
    exit 1
fi

echo "✅ Configuración verificada"
echo ""

# Crear directorios necesarios
echo "📁 Preparando directorios..."
mkdir -p data output logs
echo "✅ Directorios preparados"
echo ""

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true
echo "✅ Contenedores detenidos"
echo ""

# Limpiar imágenes antiguas
echo "🧹 Limpiando imágenes antiguas..."
docker system prune -f
echo "✅ Limpieza completada"
echo ""

# Construir nueva imagen
echo "🔨 Construyendo imagen de producción..."
docker-compose -f docker-compose.prod.yml build --no-cache
echo "✅ Imagen construida"
echo ""

# Ejecutar en modo detached
echo "🚀 Iniciando microservicio en producción..."
docker-compose -f docker-compose.prod.yml up -d
echo "✅ Microservicio iniciado"
echo ""

# Esperar un momento para que el contenedor se inicie
echo "⏳ Esperando que el contenedor se inicie..."
sleep 10

# Verificar estado
echo "📊 Verificando estado del servicio..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Microservicio ejecutándose correctamente"
else
    echo "❌ Error: El microservicio no se inició correctamente"
    echo "📋 Logs del contenedor:"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

echo ""
echo "🎉 ¡Despliegue completado exitosamente!"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Ver estado: docker-compose -f docker-compose.prod.yml ps"
echo "   Detener: docker-compose -f docker-compose.prod.yml down"
echo "   Reiniciar: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "📊 Información del contenedor:"
docker-compose -f docker-compose.prod.yml ps 