# 🚂 Microservicio Chesterton

Microservicio optimizado para procesar datos de Chesterton y sincronizarlos con Qdrant y PostgreSQL.

## 🚀 Despliegue Rápido en Railway

### 1. Crear Proyecto
1. Ve a [railway.app](https://railway.app)
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Selecciona: `minarkap/chesterton-microservice`

### 2. Configurar Variables
En Railway Dashboard → **Variables**:

```env
GOOGLE_API_KEY=tu_clave_de_google_ai_aqui
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_clave_de_qdrant_aqui
QDRANT_COLLECTION=chesterton
WORDPRESS_SITE_URL=https://chestertons-atomiun.com
DB_URL=postgresql://usuario:password@host:puerto/database
XML_URL=https://atomiunservices.mobiliagestion.es/ExportarInmueblesMobilia/fa557043af982e6b3a5a4e53f86b3724.xml
```

### 3. Ejecutar
- El servicio se ejecuta una vez y termina
- Para volver a ejecutar: Railway Dashboard → **"Redeploy"**

## 📋 Qué Hace

1. **Extrae FAQs** del PDF `faq_chesterton.pdf`
2. **Scrapea WordPress** (páginas y posts)
3. **Procesa XML** y carga a PostgreSQL
4. **Indexa en Qdrant** para búsqueda semántica

## 🔍 Verificar Funcionamiento

### Logs Esperados:
```
🚀 Iniciando Microservicio Chesterton
📋 Modo: Ejecución única optimizada
✅ Todas las variables de entorno están configuradas
✅ PDF encontrado: /app/data/faq_chesterton.pdf
📋 Ejecutando 4 scripts en secuencia...
✅ Extracción de FAQs del PDF completado exitosamente
✅ Scraping de WordPress completado exitosamente
✅ Procesamiento de XML y carga a base de datos completado exitosamente
✅ Indexación en Qdrant completado exitosamente
🎉 Procesamiento completado
```

## ⏰ Automatización

Para ejecución semanal automática, usa cron externo:

### UptimeRobot (Gratis)
- Ping semanal a tu servicio Railway
- Automático y confiable

### GitHub Actions
```yaml
name: Deploy Weekly
on:
  schedule:
    - cron: '0 2 * * 0'  # Domingo 2:00 AM
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.RAILWAY_TOKEN }}" \
            https://api.railway.app/v1/services/${{ secrets.RAILWAY_SERVICE_ID }}/deployments
```

## 💰 Costos

- **Ejecución única**: ~$0.50-2/mes
- **Servicio continuo**: $5-15/mes
- **Ahorro**: 90-95% menos costos

## 🚨 Solución de Problemas

### Variables no configuradas
```
❌ Variables de entorno faltantes: ['GOOGLE_API_KEY']
```
**Solución:** Configura todas las variables en Railway Dashboard

### PDF no encontrado
```
❌ PDF no encontrado: /app/data/faq_chesterton.pdf
```
**Solución:** El PDF está incluido en el repo, verifica el build

## 📁 Estructura

```
chesterton_microservice/
├── scripts/
│   ├── run_once_optimized.py    # Script principal
│   ├── faq_to_md.py            # Extracción PDF
│   ├── wp_chesterton.py        # Scraping WordPress
│   ├── xml_to_db.py            # Procesamiento XML
│   └── chesterton_qdrant.py    # Indexación Qdrant
├── data/
│   └── faq_chesterton.pdf      # PDF incluido
├── railway_config.py            # Entrypoint Railway
├── Dockerfile                   # Imagen Docker
├── requirements.txt             # Dependencias Python
└── env.example                  # Variables de ejemplo
```

## 🔗 Enlaces

- **Repositorio:** https://github.com/minarkap/chesterton-microservice
- **Railway:** https://railway.app
- **Guía Completa:** `RAILWAY_SINGLE_EXECUTION.md`

---

**¡Microservicio optimizado para Railway con mínimo costo! 🚂✨** 