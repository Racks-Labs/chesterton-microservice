# 🚂 Despliegue en Railway - Microservicio Chesterton

## 🎯 Configuración Específica para Railway

Este microservicio está optimizado para desplegarse en Railway con el archivo PDF incluido en el repositorio.

## 📋 Requisitos Previos

1. **Cuenta en Railway**: [railway.app](https://railway.app)
2. **Repositorio en GitHub**: Con el microservicio subido
3. **Variables de entorno**: Configuradas en Railway

## 🚀 Pasos de Despliegue

### 1. Conectar Repositorio

1. Ve a [Railway Dashboard](https://railway.app/dashboard)
2. Haz clic en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Busca y selecciona tu repositorio `chesterton-microservice`
5. Railway detectará automáticamente que es un proyecto Docker

### 2. Configurar Variables de Entorno

En Railway Dashboard → Variables:

```env
# Configuración de Google AI
GOOGLE_API_KEY=tu_google_api_key_aqui

# Configuración de Qdrant
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_qdrant_api_key_aqui
QDRANT_COLLECTION=chesterton

# Configuración de WordPress
WORDPRESS_SITE_URL=https://chestertons-atomiun.com

# Configuración de Base de Datos PostgreSQL (Railway puede crear una)
DB_URL=postgresql://usuario:password@host:puerto/base_de_datos

# Configuración de XML
XML_URL=https://atomiunservices.mobiliagestion.es/ExportarInmueblesMobilia/fa557043af982e6b3a5a4e53f86b3724.xml
```

### 3. Configurar Base de Datos (Opcional)

Si necesitas PostgreSQL:

1. En Railway Dashboard → **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway te dará la URL de conexión automáticamente
3. Copia la URL y configúrala como `DB_URL`

### 4. Desplegar

1. Railway detectará el `Dockerfile` automáticamente
2. El despliegue comenzará automáticamente
3. Puedes ver los logs en tiempo real

## 📁 Estructura para Railway

```
chesterton_microservice/
├── Dockerfile                 # Railway lo detecta automáticamente
├── docker-compose.yml         # No se usa en Railway
├── requirements.txt           # Dependencias Python
├── entrypoint.sh             # Script de entrada
├── data/
│   └── faq_chesterton.pdf    # ✅ INCLUIDO para Railway
├── scripts/                  # Scripts de procesamiento
└── .env.example              # Plantilla de configuración
```

## 🔧 Configuración Específica

### Variables Críticas para Railway

```env
# OBLIGATORIAS
GOOGLE_API_KEY=tu_clave_de_google_ai
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_clave_de_qdrant

# OPCIONALES (dependiendo de tu uso)
WORDPRESS_SITE_URL=https://chestertons-atomiun.com
DB_URL=postgresql://...  # Si usas base de datos
XML_URL=https://...      # Si procesas XML
```

### Comando de Inicio

Railway ejecutará automáticamente:
```bash
./entrypoint.sh
```

## 📊 Monitoreo

### Ver Logs en Railway

1. Ve a tu proyecto en Railway Dashboard
2. Haz clic en el servicio
3. Ve a la pestaña **"Logs"**
4. Los logs aparecerán en tiempo real

### Verificar Estado

```bash
# Los logs mostrarán:
🚀 Iniciando microservicio de Chesterton...
🔧 Variables de entorno cargadas correctamente
📋 Ejecutando: Extracción de FAQs del PDF
✅ Extracción de FAQs del PDF completado exitosamente
📋 Ejecutando: Scraping de WordPress
✅ Scraping de WordPress completado exitosamente
📋 Ejecutando: Procesamiento de XML y carga a base de datos
✅ Procesamiento de XML y carga a base de datos completado exitosamente
📋 Ejecutando: Indexación en Qdrant
✅ Indexación en Qdrant completado exitosamente
🎉 ¡Proceso completado exitosamente!
```

## 🔄 Despliegues Automáticos

Railway se conectará automáticamente a tu repositorio de GitHub y:

- **Desplegará automáticamente** cuando hagas push a `main`
- **Reconstruirá la imagen** si cambias el `Dockerfile`
- **Actualizará las variables de entorno** si las cambias en Railway

## 🐛 Solución de Problemas

### Error: "No se encontró el archivo PDF"

```bash
# Verificar que el PDF está en el repositorio
ls -la data/faq_chesterton.pdf
```

### Error: "Variables de entorno no configuradas"

1. Ve a Railway Dashboard → Variables
2. Verifica que todas las variables estén configuradas
3. Asegúrate de que no hay espacios extra

### Error: "Docker build failed"

1. Verifica que el `Dockerfile` esté en la raíz del repositorio
2. Revisa los logs de build en Railway
3. Prueba localmente: `docker build .`

### Error: "Connection to Qdrant failed"

1. Verifica `QDRANT_URL` y `QDRANT_API_KEY`
2. Asegúrate de que tu cluster de Qdrant esté activo
3. Verifica que la URL sea accesible desde Railway

## 📈 Escalabilidad

Railway permite:

- **Auto-scaling** basado en uso
- **Múltiples instancias** si es necesario
- **Monitoreo de recursos** en tiempo real
- **Backups automáticos** de la base de datos

## 💰 Costos

- **Railway**: Pay-as-you-go basado en uso
- **Qdrant**: Depende de tu plan
- **Google AI**: Depende de tu uso de embeddings

## 🎉 ¡Listo para Railway!

Tu microservicio está optimizado para Railway con:

- ✅ PDF incluido en el repositorio
- ✅ Dockerfile configurado
- ✅ Variables de entorno preparadas
- ✅ Scripts de automatización
- ✅ Documentación completa

**¡Despliega y disfruta! 🚂** 