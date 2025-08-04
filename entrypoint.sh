#!/bin/bash

# Cargar variables de entorno
set -a
source .env
set +a

echo "🚀 Iniciando microservicio de Chesterton..."

# Función para manejar errores
handle_error() {
    echo "❌ Error en el script: $1"
    exit 1
}

# Función para ejecutar un script con manejo de errores
run_script() {
    local script_name=$1
    local script_path=$2
    local description=$3
    
    echo "📋 Ejecutando: $description"
    echo "📍 Script: $script_name"
    
    if python "$script_path"; then
        echo "✅ $description completado exitosamente"
    else
        handle_error "$description falló"
    fi
    echo ""
}

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env"
    echo "📝 Copia env.example a .env y configura las variables"
    exit 1
fi

# Verificar variables de entorno críticas
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "TU_GOOGLE_API_KEY_AQUI" ]; then
    handle_error "GOOGLE_API_KEY no está configurada correctamente"
fi

if [ -z "$QDRANT_URL" ] || [ -z "$QDRANT_API_KEY" ]; then
    handle_error "Variables de Qdrant no están configuradas correctamente"
fi

echo "🔧 Variables de entorno cargadas correctamente"
echo ""

# Paso 1: Extraer FAQs del PDF
if [ -f "data/faq_chesterton.pdf" ]; then
    run_script "faq_to_md.py" "scripts/faq_to_md.py" "Extracción de FAQs del PDF"
else
    echo "⚠️ Archivo PDF de FAQs no encontrado, saltando paso 1"
fi

# Paso 2: Scrapear WordPress
run_script "wp_chesterton.py" "scripts/wp_chesterton.py" "Scraping de WordPress"

# Paso 3: Procesar XML y cargar a base de datos
if [ -n "$DB_URL" ] && [ "$DB_URL" != "postgresql://usuario:password@host:puerto/base_de_datos" ]; then
    run_script "xml_to_db.py" "scripts/xml_to_db.py" "Procesamiento de XML y carga a base de datos"
else
    echo "⚠️ URL de base de datos no configurada, saltando paso 3"
fi

# Paso 4: Indexar en Qdrant
run_script "chesterton_qdrant.py" "scripts/chesterton_qdrant.py" "Indexación en Qdrant"

echo "🎉 ¡Proceso completado exitosamente!"
echo "📊 Resumen de archivos generados:"
echo "   - FAQs: $(ls -1 faqs_markdown/*.md 2>/dev/null | wc -l | tr -d ' ') archivos"
echo "   - Páginas: $(ls -1 pages/*.md 2>/dev/null | wc -l | tr -d ' ') archivos"
echo "   - Posts: $(ls -1 posts/*.md 2>/dev/null | wc -l | tr -d ' ') archivos" 