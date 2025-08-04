# ⏰ Guía de Cron Jobs Semanales - Railway

## 🎯 **Mejor Opción: Railway Cron Jobs**

Para tu caso de uso (ejecución semanal), la **mejor opción** es usar Railway Cron Jobs. Es más eficiente en costos y más simple de configurar.

## 🚀 **Configuración en Railway**

### **Opción 1: Railway Cron Jobs (Recomendado)**

#### **1. Configurar Variables de Entorno**

En Railway Dashboard → Variables:

```env
# OBLIGATORIAS
GOOGLE_API_KEY=tu_clave_de_google_ai
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_clave_de_qdrant
QDRANT_COLLECTION=chesterton

# OPCIONALES
WORDPRESS_SITE_URL=https://chestertons-atomiun.com
DB_URL=postgresql://usuario:password@host:puerto/db
XML_URL=https://atomiunservices.mobiliagestion.es/ExportarInmueblesMobilia/fa557043af982e6b3a5a4e53f86b3724.xml

# CONFIGURACIÓN DE CRON
EXECUTION_MODE=cron
```

#### **2. Configurar Cron Job en Railway**

En Railway Dashboard:

1. Ve a tu proyecto
2. Haz clic en **"Settings"**
3. Busca la sección **"Cron Jobs"**
4. Agrega un nuevo cron job:

```
Schedule: 0 2 * * 0
Command: python scripts/cron_job.py
Description: Actualización semanal de datos Chesterton
```

**Explicación del schedule:**
- `0 2 * * 0` = Cada domingo a las 2:00 AM
- `0 0 * * 1` = Cada lunes a las 00:00 AM
- `0 6 * * 0` = Cada domingo a las 6:00 AM

#### **3. Configuraciones de Schedule Comunes**

```bash
# Cada domingo a las 2:00 AM
0 2 * * 0

# Cada lunes a las 00:00 AM
0 0 * * 1

# Cada domingo a las 6:00 AM
0 6 * * 0

# Cada 15 días a las 3:00 AM
0 3 */15 * *

# Cada mes el día 1 a las 4:00 AM
0 4 1 * *
```

### **Opción 2: Servicio Continuo con Scheduler**

Si prefieres mantener el servicio activo:

```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=168  # 7 días
```

## 💰 **Comparación de Costos**

### **Railway Cron Jobs (Recomendado)**
- ✅ **Costo**: Solo paga cuando ejecuta (~5-15 minutos/semana)
- ✅ **Recursos**: Se activa solo cuando es necesario
- ✅ **Simplicidad**: Configuración automática
- ✅ **Logs**: Centralizados en Railway

### **Servicio Continuo**
- ❌ **Costo**: Paga 24/7 (168 horas/semana)
- ❌ **Recursos**: Consume memoria y CPU constantemente
- ✅ **Ventaja**: Logs en tiempo real

## 📊 **Monitoreo de Cron Jobs**

### **Ver Logs de Cron Jobs**

1. Ve a Railway Dashboard
2. Haz clic en tu proyecto
3. Ve a **"Deployments"**
4. Busca las ejecuciones del cron job
5. Haz clic en los logs para ver detalles

### **Logs Esperados**

```
🚀 Iniciando Cron Job Semanal - Microservicio Chesterton
⏰ Inicio: 2024-01-07T02:00:00
✅ Variables de entorno verificadas
🚀 Ejecutando: Extracción de FAQs del PDF
✅ Extracción de FAQs del PDF completado exitosamente
🚀 Ejecutando: Scraping de WordPress
✅ Scraping de WordPress completado exitosamente
🚀 Ejecutando: Procesamiento de XML y carga a base de datos
✅ Procesamiento de XML y carga a base de datos completado exitosamente
🚀 Ejecutando: Indexación en Qdrant
✅ Indexación en Qdrant completado exitosamente
🎉 Cron Job Semanal Completado
⏰ Duración total: 0:12:34
📊 Resumen: 4/4 scripts ejecutados exitosamente
```

## 🔧 **Configuración Avanzada**

### **Múltiples Cron Jobs**

Puedes configurar diferentes frecuencias:

```bash
# Actualización semanal (domingo 2:00 AM)
0 2 * * 0 python scripts/cron_job.py

# Backup diario (cada día 6:00 AM)
0 6 * * * python scripts/backup.py

# Limpieza mensual (día 1, 3:00 AM)
0 3 1 * * python scripts/cleanup.py
```

### **Notificaciones**

Railway puede enviar notificaciones cuando los cron jobs fallan:

1. Ve a **"Settings"** → **"Notifications"**
2. Configura alertas para fallos de cron jobs
3. Recibe emails/Slack cuando algo falle

## 🐛 **Solución de Problemas**

### **Cron Job No Se Ejecuta**

1. Verifica el schedule en Railway Dashboard
2. Comprueba que el comando sea correcto
3. Revisa los logs de Railway

### **Cron Job Falla**

1. Revisa los logs específicos del cron job
2. Verifica las variables de entorno
3. Comprueba la conectividad de red

### **Cron Job Tarda Demasiado**

1. El script tiene timeout de 30 minutos por script
2. Considera optimizar los scripts
3. Divide en múltiples cron jobs si es necesario

## 🎯 **Configuración Recomendada Final**

### **Para Producción Semanal:**

```env
# Variables de entorno
GOOGLE_API_KEY=tu_clave
QDRANT_URL=tu_url
QDRANT_API_KEY=tu_clave
WORDPRESS_SITE_URL=https://chestertons-atomiun.com
DB_URL=tu_db_url
XML_URL=tu_xml_url

# Cron job: Cada domingo a las 2:00 AM
Schedule: 0 2 * * 0
Command: python scripts/cron_job.py
```

### **Para Testing:**

```env
# Cron job: Cada hora (para pruebas)
Schedule: 0 * * * *
Command: python scripts/cron_job.py
```

## 🎉 **Ventajas de Railway Cron Jobs**

- ✅ **Eficiencia de costos**: Solo paga cuando ejecuta
- ✅ **Simplicidad**: Configuración automática
- ✅ **Confiabilidad**: Railway maneja la infraestructura
- ✅ **Monitoreo**: Logs centralizados
- ✅ **Escalabilidad**: Fácil cambiar frecuencia
- ✅ **Notificaciones**: Alertas automáticas

---

**¡Esta es la mejor opción para tu caso de uso semanal! ⏰** 