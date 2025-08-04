# 🚀 Guía de Inicio Rápido - Microservicio Chesterton

## ⚡ Configuración en 3 Pasos

### 1. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar con tus credenciales
nano .env
```

**Variables obligatorias:**
- `GOOGLE_API_KEY`: Tu clave de API de Google AI
- `QDRANT_URL`: URL de tu cluster de Qdrant
- `QDRANT_API_KEY`: Tu clave de API de Qdrant

### 2. Ejecutar Setup Automático
```bash
./setup.sh
```

### 3. Ejecutar el Microservicio
```bash
# Opción A: Ejecución completa
./run.sh

# Opción B: Con Make
make run

# Opción C: Desarrollo (scripts individuales)
./dev.sh all
```

## 🎯 Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `./setup.sh` | Configuración inicial |
| `./run.sh` | Ejecutar microservicio completo |
| `./dev.sh all` | Ejecutar todos los scripts |
| `./dev.sh faq` | Solo extracción de FAQs |
| `./dev.sh wp` | Solo scraping WordPress |
| `./dev.sh xml` | Solo procesamiento XML |
| `./dev.sh qdrant` | Solo indexación Qdrant |
| `make help` | Ver todos los comandos |

## 📁 Estructura del Proyecto

```
chesterton_microservice/
├── 📄 Dockerfile              # Configuración Docker
├── 📄 docker-compose.yml      # Orquestación básica
├── 📄 docker-compose.dev.yml  # Desarrollo
├── 📄 docker-compose.prod.yml # Producción
├── 📄 requirements.txt        # Dependencias Python
├── 📄 entrypoint.sh          # Script principal
├── 📄 setup.sh               # Configuración inicial
├── 📄 run.sh                 # Ejecución completa
├── 📄 dev.sh                 # Desarrollo
├── 📄 deploy.sh              # Despliegue producción
├── 📄 Makefile               # Comandos Make
├── 📄 env.example            # Variables de entorno
├── 📄 README.md              # Documentación completa
├── 📄 QUICK_START.md         # Esta guía
├── 📁 scripts/               # Scripts de procesamiento
│   ├── faq_to_md.py         # Extracción FAQs
│   ├── wp_chesterton.py     # Scraping WordPress
│   ├── xml_to_db.py         # Procesamiento XML
│   └── chesterton_qdrant.py # Indexación Qdrant
└── 📁 data/                  # Datos de entrada
    └── faq_chesterton.pdf   # PDF de FAQs
```

## 🔄 Flujo de Procesamiento

1. **📖 Extracción FAQs** → `faqs_markdown/`
2. **🌐 Scraping WordPress** → `pages/` y `posts/`
3. **📊 Procesamiento XML** → Base de datos PostgreSQL
4. **🧠 Indexación Qdrant** → Embeddings y búsquedas semánticas

## 🐳 Docker

### Desarrollo
```bash
docker-compose -f docker-compose.dev.yml up
```

### Producción
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Troubleshooting

### Error: "GOOGLE_API_KEY no está configurada"
```bash
# Verificar archivo .env
cat .env | grep GOOGLE_API_KEY
```

### Error: "Docker no está ejecutándose"
```bash
# Iniciar Docker Desktop o servicio
sudo systemctl start docker
```

### Error: "No se encontró el archivo PDF"
```bash
# Verificar que existe
ls -la data/faq_chesterton.pdf
```

## 📊 Monitoreo

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver estado del contenedor
docker-compose ps

# Ver uso de recursos
docker stats
```

## 🚀 Despliegue en Producción

```bash
# Despliegue automático
./deploy.sh

# Verificar estado
docker-compose -f docker-compose.prod.yml ps
```

## 📞 Soporte

- 📖 **Documentación completa**: `README.md`
- 🔧 **Comandos Make**: `make help`
- 🐛 **Logs**: `docker-compose logs -f`
- 💻 **Shell del contenedor**: `./dev.sh shell`

---

**¡Listo para usar! 🎉** 