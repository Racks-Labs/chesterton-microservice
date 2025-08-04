#!/bin/bash

# Script para desarrollo - permite ejecutar scripts individuales

# Cargar variables de entorno
set -a
source .env
set +a

# Función para mostrar ayuda
show_help() {
    echo "🔧 Script de Desarrollo - Microservicio Chesterton"
    echo ""
    echo "Uso: ./dev.sh [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  faq          - Ejecutar solo extracción de FAQs"
    echo "  wp           - Ejecutar solo scraping de WordPress"
    echo "  xml          - Ejecutar solo procesamiento de XML"
    echo "  qdrant       - Ejecutar solo indexación en Qdrant"
    echo "  all          - Ejecutar todos los scripts en secuencia"
    echo "  shell        - Acceder al shell del contenedor"
    echo "  build        - Construir imagen Docker"
    echo "  logs         - Ver logs del contenedor"
    echo "  stop         - Detener contenedor"
    echo "  help         - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./dev.sh faq"
    echo "  ./dev.sh all"
    echo "  ./dev.sh shell"
}

# Función para ejecutar script individual
run_script() {
    local script_name=$1
    local description=$2
    
    echo "📋 Ejecutando: $description"
    echo "📍 Script: $script_name"
    
    # Construir y ejecutar contenedor para script específico
    docker-compose -f docker-compose.dev.yml build
    
    if docker-compose -f docker-compose.dev.yml run --rm chesterton-microservice python "scripts/$script_name"; then
        echo "✅ $description completado exitosamente"
    else
        echo "❌ $description falló"
        return 1
    fi
}

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encontró el archivo .env"
    echo "💡 Ejecuta ./setup.sh primero para configurar el entorno"
    exit 1
fi

# Procesar argumentos
case "${1:-help}" in
    "faq")
        run_script "faq_to_md.py" "Extracción de FAQs del PDF"
        ;;
    "wp")
        run_script "wp_chesterton.py" "Scraping de WordPress"
        ;;
    "xml")
        run_script "xml_to_db.py" "Procesamiento de XML y carga a base de datos"
        ;;
    "qdrant")
        run_script "chesterton_qdrant.py" "Indexación en Qdrant"
        ;;
    "all")
        echo "🚀 Ejecutando todos los scripts en secuencia..."
        echo ""
        
        # Ejecutar todos los scripts
        run_script "faq_to_md.py" "Extracción de FAQs del PDF" && \
        run_script "wp_chesterton.py" "Scraping de WordPress" && \
        run_script "xml_to_db.py" "Procesamiento de XML y carga a base de datos" && \
        run_script "chesterton_qdrant.py" "Indexación en Qdrant"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 ¡Todos los scripts ejecutados exitosamente!"
            echo "📊 Resumen de archivos generados:"
            echo "   - FAQs: $(ls -1 faqs_markdown/*.md 2>/dev/null | wc -l | tr -d ' ') archivos"
            echo "   - Páginas: $(ls -1 pages/*.md 2>/dev/null | wc -l | tr -d ' ') archivos"
            echo "   - Posts: $(ls -1 posts/*.md 2>/dev/null | wc -l | tr -d ' ') archivos"
        else
            echo "❌ Algunos scripts fallaron"
            exit 1
        fi
        ;;
    "shell")
        echo "🐚 Accediendo al shell del contenedor..."
        docker-compose -f docker-compose.dev.yml run --rm chesterton-microservice /bin/bash
        ;;
    "build")
        echo "🔨 Construyendo imagen Docker..."
        docker-compose -f docker-compose.dev.yml build
        ;;
    "logs")
        echo "📋 Mostrando logs..."
        docker-compose -f docker-compose.dev.yml logs -f
        ;;
    "stop")
        echo "🛑 Deteniendo contenedor..."
        docker-compose -f docker-compose.dev.yml down
        ;;
    "help"|*)
        show_help
        ;;
esac 