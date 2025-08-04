# 🚀 Guía para Subir a GitHub

## 📋 Pasos para Subir el Microservicio a GitHub

### 1. Crear Repositorio en GitHub

1. Ve a [GitHub.com](https://github.com)
2. Haz clic en **"New repository"** o **"+"** → **"New repository"**
3. Configura el repositorio:
   - **Repository name**: `chesterton-microservice`
   - **Description**: `Microservicio dockerizado para procesamiento de datos de Chesterton`
   - **Visibility**: `Public` o `Private` (según prefieras)
   - **NO** marques "Add a README file" (ya tenemos uno)
   - **NO** marques "Add .gitignore" (ya tenemos uno)
4. Haz clic en **"Create repository"**

### 2. Inicializar Git Localmente

```bash
# Navegar al directorio del microservicio
cd chesterton_microservice

# Inicializar repositorio Git
git init

# Verificar que .gitignore está funcionando
git status
```

### 3. Verificar Archivos a Subir

```bash
# Ver qué archivos se van a subir
git add -n .

# Si todo se ve bien, agregar todos los archivos
git add .

# Ver el estado
git status
```

**✅ Archivos que SÍ deben subirse:**
- `Dockerfile`
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `docker-compose.prod.yml`
- `requirements.txt`
- `entrypoint.sh`
- `setup.sh`
- `run.sh`
- `dev.sh`
- `deploy.sh`
- `Makefile`
- `env.example`
- `README.md`
- `QUICK_START.md`
- `GITHUB_SETUP.md`
- `LICENSE`
- `.gitignore`
- `scripts/` (todos los archivos .py)

**❌ Archivos que NO deben subirse:**
- `.env` (contiene credenciales)
- `data/` (datos de entrada)
- `faqs_markdown/`, `pages/`, `posts/` (datos generados)
- `output/` (datos de salida)

### 4. Hacer el Primer Commit

```bash
# Hacer commit inicial
git commit -m "🎉 Initial commit: Microservicio Chesterton dockerizado

- Extracción de FAQs desde PDF
- Scraping de WordPress
- Procesamiento de XML a PostgreSQL
- Indexación en Qdrant
- Configuración completa con Docker
- Scripts de automatización
- Documentación completa"
```

### 5. Conectar con GitHub

```bash
# Agregar el repositorio remoto (reemplaza USERNAME con tu usuario)
git remote add origin https://github.com/USERNAME/chesterton-microservice.git

# Verificar que se agregó correctamente
git remote -v
```

### 6. Subir a GitHub

```bash
# Subir al repositorio
git push -u origin main

# Si tu rama principal es 'master' en lugar de 'main':
# git push -u origin master
```

### 7. Verificar en GitHub

1. Ve a tu repositorio en GitHub
2. Verifica que todos los archivos estén subidos
3. Verifica que el archivo `.env` **NO** esté presente

## 🔧 Configuración Adicional

### Agregar Badges al README

Puedes agregar estos badges al README.md:

```markdown
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/USERNAME/chesterton-microservice)
```

### Configurar GitHub Actions (Opcional)

Si quieres CI/CD, crea `.github/workflows/docker-build.yml`:

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build Docker image
      run: docker build -t chesterton-microservice .
```

## 🚨 Importante: Seguridad

### ✅ Verificar que NO se suban credenciales

```bash
# Verificar que .env NO está en el repositorio
git ls-files | grep -E "\.env$"

# Si aparece algún archivo .env, eliminarlo
git rm --cached .env
git commit -m "🔒 Remove .env file from repository"
git push
```

### 🔐 Configurar Secrets en GitHub (Opcional)

Si usas GitHub Actions, configura secrets:
1. Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions**
2. Agrega secrets:
   - `GOOGLE_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `DB_URL`

## 📝 Comandos Útiles

```bash
# Ver estado del repositorio
git status

# Ver historial de commits
git log --oneline

# Ver archivos que se van a subir
git diff --cached

# Subir cambios futuros
git add .
git commit -m "Descripción del cambio"
git push

# Crear una nueva rama
git checkout -b feature/nueva-funcionalidad

# Cambiar a rama principal
git checkout main
```

## 🎯 Checklist Final

- [ ] Repositorio creado en GitHub
- [ ] Git inicializado localmente
- [ ] `.env` NO está en el repositorio
- [ ] Todos los archivos de código subidos
- [ ] README.md actualizado
- [ ] Primer commit realizado
- [ ] Repositorio conectado con GitHub
- [ ] Código subido exitosamente
- [ ] Verificado en GitHub

## 🆘 Solución de Problemas

### Error: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/USERNAME/chesterton-microservice.git
```

### Error: "Permission denied"
```bash
# Usar SSH en lugar de HTTPS
git remote set-url origin git@github.com:USERNAME/chesterton-microservice.git
```

### Error: "Branch 'main' does not exist"
```bash
# Crear rama main
git checkout -b main
git push -u origin main
```

---

**¡Listo! Tu microservicio está ahora en GitHub 🎉** 