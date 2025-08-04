# 🚂 Opciones Reales en Railway - Microservicio Chesterton

## 🔍 **Situación Real en Railway**

Railway **NO tiene cron jobs nativos** en las settings. Te explico las opciones reales que tienes disponibles:

## 🎯 **Opciones Disponibles**

### **Opción 1: Servicio Continuo con Scheduler (Recomendado)**

Esta es la **mejor opción** para Railway. El servicio se ejecuta continuamente pero solo procesa datos periódicamente.

#### **Configuración:**

```env
# Variables de entorno en Railway Dashboard
GOOGLE_API_KEY=tu_clave_de_google_ai
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_clave_de_qdrant
QDRANT_COLLECTION=chesterton
WORDPRESS_SITE_URL=https://chestertons-atomiun.com
DB_URL=tu_db_url
XML_URL=tu_xml_url

# CONFIGURACIÓN DE EJECUCIÓN
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=168  # 7 días
```

#### **Cómo Funciona:**
1. ✅ El servicio se despliega y se mantiene activo
2. ✅ Ejecuta inmediatamente la primera vez
3. ✅ Luego se "duerme" durante el intervalo configurado
4. ✅ Se "despierta" automáticamente para procesar
5. ✅ Logs disponibles en Railway Dashboard

#### **Ventajas:**
- ✅ **Automático**: No necesitas intervención manual
- ✅ **Logs centralizados**: Todo en Railway Dashboard
- ✅ **Configurable**: Fácil cambiar el intervalo
- ✅ **Confiabilidad**: Railway maneja la infraestructura

#### **Desventajas:**
- ❌ **Costo**: Paga por el tiempo que está activo (aunque duerme)

### **Opción 2: Ejecución Manual (Más Barato)**

Para minimizar costos, ejecuta manualmente cuando necesites:

```env
EXECUTION_MODE=once
```

#### **Cómo Usar:**
1. Configura las variables de entorno
2. El servicio se ejecuta una vez y termina
3. Para actualizar: Railway Dashboard → **"Redeploy"**

#### **Ventajas:**
- ✅ **Mínimo costo**: Solo paga cuando ejecuta
- ✅ **Control total**: Tú decides cuándo actualizar

#### **Desventajas:**
- ❌ **Manual**: Necesitas recordar ejecutar
- ❌ **No automático**: Sin actualizaciones automáticas

### **Opción 3: Servicios Externos de Cron**

Puedes usar servicios externos para "despertar" tu servicio:

#### **Opción A: UptimeRobot**
1. Configura `EXECUTION_MODE=once`
2. Usa UptimeRobot para hacer ping a tu servicio
3. Configura el ping cada semana

#### **Opción B: GitHub Actions**
1. Crea un workflow que haga deploy automático
2. Programa el workflow con cron en GitHub
3. Se ejecuta semanalmente

## 🚀 **Configuración Recomendada**

### **Para Producción (Recomendado):**

```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=168  # 7 días
```

### **Para Desarrollo/Testing:**

```env
EXECUTION_MODE=once
```

### **Para Minimizar Costos:**

```env
EXECUTION_MODE=once
# + UptimeRobot o GitHub Actions para automatizar
```

## 📊 **Comparación de Costos**

### **Servicio Continuo con Scheduler**
- **Costo**: ~$5-15/mes (dependiendo del plan)
- **Uso**: 24/7 pero "durmiente" la mayor parte del tiempo
- **Ventaja**: Completamente automático

### **Ejecución Manual**
- **Costo**: ~$0.50-2/mes (solo cuando ejecuta)
- **Uso**: 5-15 minutos por ejecución
- **Ventaja**: Mínimo costo

### **Servicios Externos**
- **Costo**: $0-5/mes (dependiendo del servicio)
- **Uso**: Ping semanal + tiempo de ejecución
- **Ventaja**: Balance entre costo y automatización

## 🔧 **Configuración Paso a Paso**

### **1. Desplegar en Railway**

1. Ve a [railway.app](https://railway.app)
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Selecciona tu repositorio: `minarkap/chesterton-microservice`

### **2. Configurar Variables de Entorno**

En Railway Dashboard → Variables:

```env
GOOGLE_API_KEY=tu_clave_de_google_ai
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_clave_de_qdrant
QDRANT_COLLECTION=chesterton
WORDPRESS_SITE_URL=https://chestertons-atomiun.com
DB_URL=tu_db_url
XML_URL=tu_xml_url
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=168
```

### **3. Monitorear Logs**

Los logs mostrarán:

```
🚀 Iniciando Microservicio Chesterton (Modo Scheduler para Railway)
⏰ Configurado para ejecutar cada 168 horas
🚀 Ejecutando primera vez inmediatamente...
🔄 Iniciando procesamiento de datos
✅ Extracción de FAQs del PDF completado exitosamente
✅ Scraping de WordPress completado exitosamente
✅ Procesamiento de XML y carga a base de datos completado exitosamente
✅ Indexación en Qdrant completado exitosamente
🎉 Procesamiento completado
⏰ Duración total: 0:12:34
😴 Durmiendo 604800 segundos...
⏰ Próxima ejecución programada: 2024-01-14T02:00:00
```

## 🎯 **Recomendación Final**

**Para tu caso de uso semanal, recomiendo:**

1. **Empezar con `EXECUTION_MODE=scheduled`** para automatización completa
2. **Monitorear los costos** durante el primer mes
3. **Si los costos son altos**, cambiar a `EXECUTION_MODE=once` + servicio externo

**Configuración inicial recomendada:**
```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=168  # 7 días
```

---

**¡Esta es la configuración real que funciona en Railway! 🚂** 