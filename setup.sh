#!/bin/bash

echo "🚀 Configurando Microservicio Chesterton..."
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado. Por favor, instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose no está instalado. Por favor, instala Docker Compose primero."
    exit 1
fi

echo "✅ Docker y Docker Compose están instalados"
echo ""

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde env.example..."
    cp env.example .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales antes de continuar"
    echo "   nano .env"
    echo ""
    echo "🔑 Variables que necesitas configurar:"
    echo "   - GOOGLE_API_KEY: Tu clave de API de Google AI"
    echo "   - QDRANT_URL: URL de tu cluster de Qdrant"
    echo "   - QDRANT_API_KEY: Tu clave de API de Qdrant"
    echo "   - DB_URL: URL de tu base de datos PostgreSQL (opcional)"
    echo ""
    echo "💡 Una vez configurado, ejecuta: ./run.sh"
    exit 0
else
    echo "✅ Archivo .env ya existe"
fi

# Verificar que las variables críticas estén configuradas
echo "🔍 Verificando configuración..."

source .env

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "TU_GOOGLE_API_KEY_AQUI" ]; then
    echo "❌ Error: GOOGLE_API_KEY no está configurada correctamente"
    echo "   Edita el archivo .env y configura tu clave de Google AI"
    exit 1
fi

if [ -z "$QDRANT_URL" ] || [ "$QDRANT_URL" = "https://tu-cluster.qdrant.io:6333" ]; then
    echo "❌ Error: QDRANT_URL no está configurada correctamente"
    echo "   Edita el archivo .env y configura la URL de tu cluster de Qdrant"
    exit 1
fi

if [ -z "$QDRANT_API_KEY" ] || [ "$QDRANT_API_KEY" = "tu_qdrant_api_key_aqui" ]; then
    echo "❌ Error: QDRANT_API_KEY no está configurada correctamente"
    echo "   Edita el archivo .env y configura tu clave de API de Qdrant"
    exit 1
fi

echo "✅ Configuración básica verificada"
echo ""

# Verificar que el archivo PDF existe
if [ ! -f "data/faq_chesterton.pdf" ]; then
    echo "⚠️  Advertencia: No se encontró el archivo data/faq_chesterton.pdf"
    echo "   El script de FAQs se saltará si no está presente"
    echo ""
else
    echo "✅ Archivo PDF de FAQs encontrado"
fi

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p data output faqs_markdown pages posts
echo "✅ Directorios creados"

echo ""
echo "🎉 Configuración completada exitosamente!"
echo ""
echo "📋 Para ejecutar el microservicio:"
echo "   ./run.sh"
echo ""
echo "📋 Para ver logs:"
echo "   docker-compose logs -f"
echo ""
echo "📋 Para detener el servicio:"
echo "   docker-compose down" 