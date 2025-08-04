# Microservicio Chesterton

Este microservicio dockerizado automatiza el procesamiento completo de datos de Chesterton, incluyendo la extracción de FAQs, scraping de WordPress, procesamiento de XML y indexación en Qdrant.

## 🚀 Características

- **Extracción de FAQs**: Convierte PDFs de preguntas frecuentes a archivos Markdown
- **Scraping de WordPress**: Extrae posts y páginas de sitios WordPress
- **Procesamiento de XML**: Procesa feeds XML de propiedades inmobiliarias
- **Indexación en Qdrant**: Crea embeddings y los indexa en Qdrant para búsquedas semánticas
- **Configuración por variables de entorno**: Todas las claves de API se configuran de forma segura

## 📁 Estructura del Proyecto

```
chesterton_microservice/
├── Dockerfile                 # Configuración de Docker
├── docker-compose.yml         # Orquestación de servicios
├── docker-compose.dev.yml     # Configuración para desarrollo
├── docker-compose.prod.yml    # Configuración para producción
├── requirements.txt           # Dependencias de Python
├── entrypoint.sh             # Script de entrada principal
├── setup.sh                  # Configuración inicial
├── run.sh                    # Ejecución completa
├── dev.sh                    # Script para desarrollo
├── deploy.sh                 # Despliegue en producción
├── github_push.sh            # Script para subir a GitHub
├── Makefile                  # Comandos Make
├── env.example               # Ejemplo de configuración
├── README.md                 # Este archivo
├── QUICK_START.md            # Guía de inicio rápido
├── GITHUB_SETUP.md           # Guía para subir a GitHub
├── LICENSE                   # Licencia MIT
├── scripts/                  # Scripts de procesamiento
│   ├── chesterton_qdrant.py  # Indexación en Qdrant
│   ├── wp_chesterton.py      # Scraping de WordPress
│   ├── faq_to_md.py          # Extracción de FAQs
│   └── xml_to_db.py          # Procesamiento de XML
└── data/                     # Datos de entrada (PDFs, etc.)
```

## 🛠️ Instalación y Configuración

### 1. Clonar y configurar

```bash
# Copiar el archivo de ejemplo de configuración
cp env.example .env

# Editar el archivo .env con tus credenciales
nano .env
```

### 2. Configurar variables de entorno

Edita el archivo `.env` con tus credenciales:

```env
# Configuración de Google AI
GOOGLE_API_KEY=tu_google_api_key_aqui

# Configuración de Qdrant
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_qdrant_api_key_aqui
QDRANT_COLLECTION=chesterton

# Configuración de WordPress
WORDPRESS_SITE_URL=https://chestertons-atomiun.com

# Configuración de Base de Datos PostgreSQL
DB_URL=postgresql://usuario:password@host:puerto/base_de_datos

# Configuración de XML
XML_URL=https://atomiunservices.mobiliagestion.es/ExportarInmueblesMobilia/fa557043af982e6b3a5a4e53f86b3724.xml
```

### 3. Preparar datos de entrada

Coloca los archivos necesarios en la carpeta `data/`:

```bash
mkdir -p data
# Copia tu archivo PDF de FAQs
cp ruta/a/tu/faq_chesterton.pdf data/
```

## 🐳 Ejecución con Docker

### Opción 1: Docker Compose (Recomendado)

```bash
# Construir y ejecutar el microservicio
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener el servicio
docker-compose down
```

### Opción 2: Docker directo

```bash
# Construir la imagen
docker build -t chesterton-microservice .

# Ejecutar el contenedor
docker run --env-file .env -v $(pwd)/data:/app/data chesterton-microservice
```

## 📋 Flujo de Procesamiento

El microservicio ejecuta los siguientes pasos en secuencia:

1. **Extracción de FAQs** (`faq_to_md.py`)
   - Lee el archivo PDF de FAQs desde `data/faq_chesterton.pdf`
   - Extrae preguntas y respuestas
   - Genera archivos Markdown en `faqs_markdown/`

2. **Scraping de WordPress** (`wp_chesterton.py`)
   - Conecta con la API REST de WordPress
   - Extrae posts y páginas
   - Convierte HTML a Markdown
   - Guarda en `posts/` y `pages/`

3. **Procesamiento de XML** (`xml_to_db.py`)
   - Descarga el feed XML de propiedades
   - Procesa y estructura los datos
   - Inserta en la base de datos PostgreSQL

4. **Indexación en Qdrant** (`chesterton_qdrant.py`)
   - Lee todos los archivos Markdown generados
   - Crea embeddings usando Google AI
   - Indexa en la colección de Qdrant

## 🔧 Configuración Avanzada

### Variables de Entorno Opcionales

- `QDRANT_COLLECTION`: Nombre de la colección en Qdrant (por defecto: "chesterton")
- `WORDPRESS_SITE_URL`: URL del sitio WordPress a scrapear

### Volúmenes Montados

- `./data:/app/data`: Datos de entrada (PDFs, etc.)
- `./output:/app/output`: Datos de salida (opcional)

## 📊 Monitoreo y Logs

### Ver logs en tiempo real

```bash
# Con Docker Compose
docker-compose logs -f

# Con Docker directo
docker logs -f <container_id>
```

### Verificar estado del contenedor

```bash
docker-compose ps
docker ps
```

## 🐛 Solución de Problemas

### Error: "GOOGLE_API_KEY no está configurada"

```bash
# Verificar que el archivo .env existe y tiene la clave correcta
cat .env | grep GOOGLE_API_KEY
```

### Error: "No se encontró el archivo PDF"

```bash
# Verificar que el archivo existe en la carpeta data
ls -la data/
```

### Error de conexión a Qdrant

```bash
# Verificar las credenciales de Qdrant
cat .env | grep QDRANT
```

### Error de conexión a la base de datos

```bash
# Verificar la URL de la base de datos
cat .env | grep DB_URL
```

## 🚀 Subir a GitHub

### Opción 1: Script Automatizado (Recomendado)

```bash
# Ejecutar el script automatizado
./github_push.sh
```

### Opción 2: Manual

1. **Crear repositorio en GitHub**
2. **Inicializar Git localmente**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
3. **Conectar con GitHub**
   ```bash
   git remote add origin https://github.com/USERNAME/chesterton-microservice.git
   git push -u origin main
   ```

### ⚠️ Importante: Seguridad

- **NUNCA** subas el archivo `.env` a GitHub
- El archivo `.env` está incluido en `.gitignore`
- Usa variables de entorno en tu servidor de producción

Para más detalles, consulta [GITHUB_SETUP.md](GITHUB_SETUP.md).

## 🔒 Seguridad

- **Nunca** commits el archivo `.env` al repositorio
- Usa variables de entorno para todas las credenciales
- El archivo `.env` está incluido en `.gitignore`

## 📝 Logs y Salida

El microservicio genera logs detallados que incluyen:

- Progreso de cada paso del procesamiento
- Número de archivos procesados
- Errores y advertencias
- Resumen final con estadísticas

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🚂 Despliegue en Railway

Para desplegar en Railway (con el PDF incluido):

1. **Sube el repositorio a GitHub** (incluye el PDF)
2. **Conecta Railway a tu repositorio**
3. **Configura las variables de entorno en Railway**
4. **¡Listo! Railway detectará el Dockerfile automáticamente**

Consulta [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) para instrucciones detalladas.

## 📚 Documentación Adicional

- [Guía de Inicio Rápido](QUICK_START.md) - Configuración en 3 pasos
- [Guía para Subir a GitHub](GITHUB_SETUP.md) - Instrucciones detalladas
- [Despliegue en Railway](RAILWAY_DEPLOYMENT.md) - Configuración específica
- [Makefile](Makefile) - Comandos útiles con `make` 