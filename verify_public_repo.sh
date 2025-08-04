#!/bin/bash

# Script para verificar que el repositorio está listo para ser público

echo "🔍 Verificando preparación para repositorio público..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "Dockerfile" ] || [ ! -f "README.md" ]; then
    echo "❌ Error: No estás en el directorio del microservicio"
    exit 1
fi

echo "✅ Directorio correcto"
echo ""

# Verificar archivos críticos
echo "📋 Verificando archivos críticos..."

critical_files=(
    "Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    "README.md"
    "LICENSE"
    ".gitignore"
    "env.example"
    "scripts/chesterton_qdrant.py"
    "scripts/wp_chesterton.py"
    "scripts/faq_to_md.py"
    "scripts/xml_to_db.py"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (FALTANTE)"
    fi
done

echo ""

# Verificar que NO hay archivos sensibles
echo "🔒 Verificando seguridad..."

sensitive_files=(
    ".env"
    ".env.local"
    ".env.production"
)

for file in "${sensitive_files[@]}"; do
    if [ -f "$file" ]; then
        echo "⚠️  $file (PRESENTE - verificar si debe estar en .gitignore)"
    else
        echo "✅ $file (NO presente - correcto)"
    fi
done

# Verificar PDF específicamente
if [ -f "data/faq_chesterton.pdf" ]; then
    echo "✅ data/faq_chesterton.pdf (PRESENTE - necesario para Railway)"
else
    echo "⚠️  data/faq_chesterton.pdf (NO presente - necesario para Railway)"
fi

echo ""

# Verificar .gitignore
echo "📝 Verificando .gitignore..."

if grep -q "\.env" .gitignore; then
    echo "✅ .env está en .gitignore"
else
    echo "❌ .env NO está en .gitignore"
fi

if grep -q "data/" .gitignore; then
    echo "✅ data/ está en .gitignore"
else
    echo "❌ data/ NO está en .gitignore"
fi

if grep -q "faqs_markdown/" .gitignore; then
    echo "✅ faqs_markdown/ está en .gitignore"
else
    echo "❌ faqs_markdown/ NO está en .gitignore"
fi

echo ""

# Verificar contenido de env.example
echo "🔑 Verificando env.example..."

if grep -q "TU_GOOGLE_API_KEY_AQUI" env.example; then
    echo "✅ env.example tiene placeholders seguros"
else
    echo "⚠️  env.example podría tener credenciales reales"
fi

echo ""

# Verificar README
echo "📖 Verificando README..."

if grep -q "Variables de entorno" README.md; then
    echo "✅ README menciona variables de entorno"
else
    echo "⚠️  README no menciona variables de entorno"
fi

if grep -q "\.env" README.md; then
    echo "✅ README menciona archivo .env"
else
    echo "⚠️  README no menciona archivo .env"
fi

echo ""

# Verificar scripts
echo "🔧 Verificando scripts..."

if [ -f "github_push.sh" ] && [ -x "github_push.sh" ]; then
    echo "✅ github_push.sh existe y es ejecutable"
else
    echo "❌ github_push.sh no existe o no es ejecutable"
fi

if [ -f "setup.sh" ] && [ -x "setup.sh" ]; then
    echo "✅ setup.sh existe y es ejecutable"
else
    echo "❌ setup.sh no existe o no es ejecutable"
fi

echo ""

# Resumen final
echo "🎯 RESUMEN PARA REPOSITORIO PÚBLICO:"
echo ""

if [ ! -f ".env" ] && [ -f ".gitignore" ] && [ -f "env.example" ]; then
    echo "✅ SEGURO para repositorio público"
    echo "   - No hay archivo .env"
    echo "   - .gitignore está configurado"
    echo "   - env.example tiene placeholders"
    echo ""
    echo "🚀 Puedes proceder con:"
    echo "   ./github_push.sh"
else
    echo "❌ NO SEGURO para repositorio público"
    echo "   - Verifica los problemas arriba"
    echo "   - No subas hasta resolverlos"
fi

echo ""
echo "📋 Checklist final:"
echo "   [ ] No hay archivo .env"
echo "   [ ] .gitignore incluye archivos sensibles"
echo "   [ ] env.example tiene placeholders"
echo "   [ ] README tiene instrucciones de configuración"
echo "   [ ] LICENSE está presente"
echo "   [ ] Todos los scripts están presentes" 