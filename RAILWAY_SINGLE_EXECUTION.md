# 🚂 Despliegue en Railway - Ejecución Única Optimizada

## 🎯 **Configuración Recomendada para Cron Externo**

Esta configuración es **ideal para cron externo** y **minimiza costos** en Railway.

## 🚀 **Paso a Paso del Despliegue**

### **1. Crear Proyecto en Railway**

1. Ve a [railway.app](https://railway.app)
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Selecciona: `minarkap/chesterton-microservice`
4. **"Deploy Now"**

### **2. Configurar Variables de Entorno**

En Railway Dashboard → **Variables**:

```env
# API Keys (OBLIGATORIAS)
GOOGLE_API_KEY=tu_clave_de_google_ai_aqui
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_clave_de_qdrant_aqui
QDRANT_COLLECTION=chesterton

# URLs de Datos (OBLIGATORIAS)
WORDPRESS_SITE_URL=https://chestertons-atomiun.com
DB_URL=postgresql://usuario:password@host:puerto/database
XML_URL=https://atomiunservices.mobiliagestion.es/ExportarInmueblesMobilia/fa557043af982e6b3a5a4e53f86b3724.xml

# CONFIGURACIÓN DE EJECUCIÓN
EXECUTION_MODE=once
```

### **3. Verificar el Despliegue**

1. Ve a **"Deployments"** → Verifica build exitoso
2. Ve a **"Logs"** → Deberías ver:

```
🚀 Iniciando Microservicio Chesterton
📋 Modo de ejecución: once
🔄 Modo: Ejecución única optimizada
🔍 Verificando variables de entorno...
✅ GOOGLE_API_KEY: Configurado
✅ QDRANT_URL: Configurado
✅ QDRANT_API_KEY: Configurado
✅ WORDPRESS_SITE_URL: Configurado
✅ DB_URL: Configurado
✅ XML_URL: Configurado
✅ Todas las variables de entorno están configuradas
✅ PDF encontrado: /app/data/faq_chesterton.pdf
📋 Ejecutando 4 scripts en secuencia...
📝 [1/4] Extracción de FAQs del PDF
🚀 Ejecutando: Extracción de FAQs del PDF
✅ Extracción de FAQs del PDF completado exitosamente
📝 [2/4] Scraping de WordPress
🚀 Ejecutando: Scraping de WordPress
✅ Scraping de WordPress completado exitosamente
📝 [3/4] Procesamiento de XML y carga a base de datos
🚀 Ejecutando: Procesamiento de XML y carga a base de datos
✅ Procesamiento de XML y carga a base de datos completado exitosamente
📝 [4/4] Indexación en Qdrant
🚀 Ejecutando: Indexación en Qdrant
✅ Indexación en Qdrant completado exitosamente
🎉 Procesamiento completado
⏰ Duración total: 0:12:34
📊 Resumen: 4/4 scripts ejecutados exitosamente
✅ Todos los scripts se ejecutaron exitosamente
🔄 El servicio terminará ahora. Para volver a ejecutar, haz redeploy.
```

## 🔄 **Cómo Ejecutar Manualmente**

### **Opción 1: Railway Dashboard**
1. Railway Dashboard → Tu proyecto
2. **"Deployments"** → **"Redeploy"**
3. El servicio se ejecutará una vez y terminará

### **Opción 2: Railway CLI**
```bash
railway up
```

## ⏰ **Configurar Cron Externo**

### **Opción A: UptimeRobot (Gratis)**
1. Ve a [uptimerobot.com](https://uptimerobot.com)
2. Crea cuenta gratuita
3. **"Add New Monitor"**
4. **Monitor Type**: HTTP(s)
5. **URL**: Tu URL de Railway
6. **Check Interval**: 7 días
7. **Alert When**: Down

### **Opción B: GitHub Actions (Gratis)**
Crea `.github/workflows/railway-deploy.yml`:

```yaml
name: Deploy to Railway Weekly

on:
  schedule:
    - cron: '0 2 * * 0'  # Cada domingo a las 2:00 AM

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.RAILWAY_TOKEN }}" \
            https://api.railway.app/v1/services/${{ secrets.RAILWAY_SERVICE_ID }}/deployments
```

### **Opción C: Cron en tu servidor**
```bash
# Añadir a crontab
0 2 * * 0 curl -X POST https://api.railway.app/v1/services/TU_SERVICE_ID/deployments \
  -H "Authorization: Bearer TU_RAILWAY_TOKEN"
```

## 📊 **Ventajas de Ejecución Única**

### **✅ Ventajas:**
- **Mínimo costo**: Solo paga cuando ejecuta (~5-15 min)
- **Control total**: Tú decides cuándo ejecutar
- **Logs claros**: Fácil verificar si funcionó
- **Sin dependencias**: No necesita servicios externos
- **Automático**: Con cron externo

### **❌ Desventajas:**
- **Manual**: Necesitas configurar cron externo
- **Dependencia externa**: Si falla el cron, no se ejecuta

## 🎯 **Configuración Recomendada**

### **Para Producción:**
```env
EXECUTION_MODE=once
# + UptimeRobot o GitHub Actions para cron
```

### **Para Testing:**
```env
EXECUTION_MODE=once
# Ejecutar manualmente desde Railway Dashboard
```

## 🔍 **Cómo Verificar que Funciona**

### **1. Verificar Logs**
Los logs deben mostrar:
- ✅ Todas las variables configuradas
- ✅ PDF encontrado
- ✅ 4/4 scripts ejecutados exitosamente
- ✅ Duración total (normalmente 5-15 minutos)

### **2. Verificar Qdrant**
- Ve a tu cluster Qdrant
- Verifica que la colección `chesterton` tenga datos
- Los embeddings deberían estar indexados

### **3. Verificar Base de Datos**
- Conecta a tu PostgreSQL
- Verifica que las tablas tengan datos actualizados

### **4. Verificar Archivos Generados**
- `faqs_markdown/` - FAQs extraídas del PDF
- `pages/` - Páginas de WordPress
- `posts/` - Posts de WordPress

## 🚨 **Solución de Problemas**

### **Error: Variables no configuradas**
```
❌ Variables de entorno faltantes: ['GOOGLE_API_KEY']
```
**Solución:** Configura todas las variables en Railway Dashboard

### **Error: PDF no encontrado**
```
❌ PDF no encontrado: /app/data/faq_chesterton.pdf
```
**Solución:** El PDF está incluido en el repo, verifica el build

### **Error: Timeout**
```
⏰ Script excedió el tiempo límite (30 min)
```
**Solución:** Railway tiene límites, pero 30 min debería ser suficiente

### **Error: Script falló**
```
❌ Scraping de WordPress falló
```
**Solución:** Revisa los logs específicos del script que falló

## 💰 **Costos Estimados**

### **Ejecución Semanal:**
- **Tiempo de ejecución**: ~5-15 minutos
- **Frecuencia**: 1 vez por semana
- **Costo mensual**: ~$0.50-2 (solo cuando ejecuta)

### **Comparación:**
- **Servicio continuo**: $5-15/mes
- **Ejecución única**: $0.50-2/mes
- **Ahorro**: 90-95% menos costos

## 🎉 **¡Listo para Producción!**

Con esta configuración tendrás:
- ✅ Ejecución automática semanal
- ✅ Mínimo costo en Railway
- ✅ Logs claros y verificables
- ✅ Control total sobre cuándo ejecutar

**¡Tu microservicio está optimizado para cron externo! 🚂✨** 