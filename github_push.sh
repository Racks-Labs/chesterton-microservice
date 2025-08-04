#!/bin/bash

# Script para subir automáticamente el microservicio a GitHub

set -e  # Salir en caso de error

echo "🚀 Preparando subida a GitHub..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "Dockerfile" ] || [ ! -f "README.md" ]; then
    echo "❌ Error: No estás en el directorio del microservicio"
    echo "💡 Navega a chesterton_microservice/ y ejecuta este script"
    exit 1
fi

# Verificar que Git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git no está instalado"
    exit 1
fi

# Verificar que no hay archivo .env
if [ -f ".env" ]; then
    echo "⚠️  Advertencia: Se encontró archivo .env"
    echo "🔒 Este archivo NO debe subirse a GitHub por seguridad"
    echo ""
    read -p "¿Quieres continuar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Operación cancelada"
        exit 1
    fi
fi

# Inicializar Git si no está inicializado
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositorio Git..."
    git init
    echo "✅ Repositorio Git inicializado"
else
    echo "✅ Repositorio Git ya existe"
fi

# Verificar estado actual
echo ""
echo "📋 Estado actual del repositorio:"
git status --porcelain

# Agregar archivos
echo ""
echo "📦 Agregando archivos al repositorio..."
git add .

# Verificar qué se va a subir
echo ""
echo "📋 Archivos que se van a subir:"
git diff --cached --name-only

# Verificar que .env NO está incluido
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ ERROR: El archivo .env está incluido en el commit"
    echo "🔒 Esto es un riesgo de seguridad"
    echo ""
    echo "💡 Soluciones:"
    echo "   1. Verifica que .env está en .gitignore"
    echo "   2. Elimina .env del staging: git reset .env"
    echo "   3. Ejecuta este script nuevamente"
    exit 1
fi

echo ""
echo "✅ Verificación de seguridad completada"

# Solicitar mensaje de commit
echo ""
echo "💬 Mensaje de commit:"
echo "   (Presiona Enter para usar el mensaje por defecto)"
read -p "Mensaje: " commit_message

if [ -z "$commit_message" ]; then
    commit_message="🎉 Initial commit: Microservicio Chesterton dockerizado

- Extracción de FAQs desde PDF
- Scraping de WordPress
- Procesamiento de XML a PostgreSQL
- Indexación en Qdrant
- Configuración completa con Docker
- Scripts de automatización
- Documentación completa"
fi

# Hacer commit
echo ""
echo "💾 Haciendo commit..."
git commit -m "$commit_message"
echo "✅ Commit realizado"

# Solicitar URL del repositorio
echo ""
echo "🌐 URL del repositorio en GitHub:"
echo "   Ejemplo: https://github.com/tu-usuario/chesterton-microservice.git"
read -p "URL: " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ Error: Debes proporcionar la URL del repositorio"
    exit 1
fi

# Configurar remoto
echo ""
echo "🔗 Configurando repositorio remoto..."
if git remote get-url origin &> /dev/null; then
    echo "🔄 Actualizando remoto existente..."
    git remote set-url origin "$repo_url"
else
    echo "➕ Agregando nuevo remoto..."
    git remote add origin "$repo_url"
fi

# Verificar remoto
echo ""
echo "📋 Repositorios remotos configurados:"
git remote -v

# Determinar rama principal
main_branch="main"
if ! git show-ref --verify --quiet refs/heads/main; then
    if git show-ref --verify --quiet refs/heads/master; then
        main_branch="master"
    else
        echo "📝 Creando rama main..."
        git checkout -b main
    fi
fi

# Subir a GitHub
echo ""
echo "🚀 Subiendo a GitHub..."
git push -u origin "$main_branch"

echo ""
echo "🎉 ¡Subida completada exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Ve a tu repositorio en GitHub: $repo_url"
echo "   2. Verifica que todos los archivos estén subidos"
echo "   3. Verifica que NO hay archivo .env"
echo "   4. Configura las variables de entorno en tu servidor"
echo ""
echo "🔐 Recuerda: Nunca subas el archivo .env a GitHub"
echo "   Usa variables de entorno en tu servidor de producción" 