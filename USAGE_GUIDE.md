# 📖 Guía de Uso - Microservicio Chesterton

## 🚂 Despliegue en Railway

### 1. **Configurar Variables de Entorno**

En Railway Dashboard → Variables, configura:

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

# CONFIGURACIÓN DE EJECUCIÓN
EXECUTION_MODE=once
EXECUTION_INTERVAL_HOURS=24
```

### 2. **Modos de Ejecución**

#### **Modo 1: Ejecución Única (Recomendado para empezar)**
```env
EXECUTION_MODE=once
```
- ✅ Se ejecuta una sola vez y termina
- ✅ Ideal para pruebas y ejecuciones manuales
- ✅ Menor consumo de recursos
- ✅ Logs claros y concisos

#### **Modo 2: Ejecución Programada (Para producción)**
```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=24
```
- ✅ Se ejecuta automáticamente cada X horas
- ✅ Mantiene datos actualizados
- ✅ Ideal para producción
- ✅ Mayor consumo de recursos

#### **Modo 3: Modo Manual (Para debugging)**
```env
EXECUTION_MODE=manual
```
- ✅ Usa el entrypoint.sh original
- ✅ Más control sobre la ejecución
- ✅ Ideal para debugging

## 🔄 **Cómo Funciona el Servicio**

### **Flujo de Procesamiento**

1. **📖 Extracción de FAQs**
   - Lee `data/faq_chesterton.pdf`
   - Extrae preguntas y respuestas
   - Genera archivos en `faqs_markdown/`

2. **🌐 Scraping de WordPress**
   - Conecta a la API REST de WordPress
   - Extrae posts y páginas
   - Convierte HTML a Markdown
   - Guarda en `posts/` y `pages/`

3. **📊 Procesamiento de XML**
   - Descarga el feed XML de propiedades
   - Procesa y estructura los datos
   - Inserta en PostgreSQL (si DB_URL está configurado)

4. **🧠 Indexación en Qdrant**
   - Lee todos los archivos Markdown
   - Crea embeddings con Google AI
   - Indexa en la colección de Qdrant

### **Logs de Ejecución**

Los logs mostrarán algo como:

```
🚀 Iniciando Microservicio Chesterton
📋 Modo de ejecución: once
✅ Variables de entorno verificadas
🚀 Ejecutando: Extracción de FAQs del PDF
✅ Extracción de FAQs del PDF completado exitosamente
🚀 Ejecutando: Scraping de WordPress
✅ Scraping de WordPress completado exitosamente
🚀 Ejecutando: Procesamiento de XML y carga a base de datos
✅ Procesamiento de XML y carga a base de datos completado exitosamente
🚀 Ejecutando: Indexación en Qdrant
✅ Indexación en Qdrant completado exitosamente
🎉 Proceso completado
📊 Resumen: 4/4 scripts ejecutados exitosamente
```

## 🔧 **Configuración Avanzada**

### **Variables de Entorno Detalladas**

```env
# CONFIGURACIÓN DE GOOGLE AI
GOOGLE_API_KEY=tu_clave_de_google_ai

# CONFIGURACIÓN DE QDRANT
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_clave_de_qdrant
QDRANT_COLLECTION=chesterton

# CONFIGURACIÓN DE WORDPRESS
WORDPRESS_SITE_URL=https://chestertons-atomiun.com

# CONFIGURACIÓN DE BASE DE DATOS
DB_URL=postgresql://usuario:password@host:puerto/db

# CONFIGURACIÓN DE XML
XML_URL=https://atomiunservices.mobiliagestion.es/ExportarInmueblesMobilia/fa557043af982e6b3a5a4e53f86b3724.xml

# CONFIGURACIÓN DE EJECUCIÓN
EXECUTION_MODE=once                    # once, scheduled, manual
EXECUTION_INTERVAL_HOURS=24            # Solo para modo scheduled
```

### **Configuraciones Recomendadas por Caso de Uso**

#### **Para Pruebas/Desarrollo**
```env
EXECUTION_MODE=once
```

#### **Para Producción con Actualizaciones Diarias**
```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=24
```

#### **Para Actualizaciones Cada 6 Horas**
```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=6
```

#### **Para Actualizaciones Semanales**
```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=168  # 7 días * 24 horas
```

## 📊 **Monitoreo y Logs**

### **Ver Logs en Railway**

1. Ve a tu proyecto en Railway Dashboard
2. Haz clic en el servicio
3. Ve a la pestaña **"Logs"**
4. Los logs aparecerán en tiempo real

### **Logs Importantes a Monitorear**

- ✅ **"Variables de entorno verificadas"** - Configuración correcta
- ✅ **"X/Y scripts ejecutados exitosamente"** - Proceso completo
- ❌ **"Variables de entorno faltantes"** - Error de configuración
- ❌ **"Script X falló"** - Error en procesamiento

### **Métricas de Rendimiento**

- **Tiempo de ejecución**: Típicamente 5-15 minutos
- **Uso de memoria**: ~500MB-1GB durante la ejecución
- **Uso de CPU**: Picos durante el procesamiento de embeddings

## 🔄 **Actualización de Datos**

### **Actualización Manual**

Para forzar una actualización manual:

1. Ve a Railway Dashboard
2. Haz clic en tu servicio
3. Ve a **"Settings"** → **"Redeploy"**
4. El servicio se ejecutará nuevamente

### **Actualización Automática**

Con `EXECUTION_MODE=scheduled`:

- Los datos se actualizarán automáticamente
- Puedes ver el historial en los logs
- Railway mantendrá el servicio activo

### **Actualización por Cambios en el Código**

- Haz push a tu repositorio de GitHub
- Railway detectará los cambios automáticamente
- Se desplegará la nueva versión
- Se ejecutará el proceso con el código actualizado

## 🐛 **Solución de Problemas**

### **Error: "Variables de entorno faltantes"**

```bash
# Verificar en Railway Dashboard → Variables
GOOGLE_API_KEY=tu_clave
QDRANT_URL=tu_url
QDRANT_API_KEY=tu_clave
```

### **Error: "Script X falló"**

1. Revisa los logs específicos del script
2. Verifica las credenciales de los servicios externos
3. Comprueba la conectividad de red

### **Error: "Connection to Qdrant failed"**

1. Verifica `QDRANT_URL` y `QDRANT_API_KEY`
2. Asegúrate de que tu cluster de Qdrant esté activo
3. Comprueba que la URL sea accesible desde Railway

### **Error: "No se encontró el archivo PDF"**

1. Verifica que `data/faq_chesterton.pdf` esté en el repositorio
2. Comprueba que el archivo no esté corrupto

### **Servicio se Detiene Inesperadamente**

1. Revisa los logs para errores
2. Verifica el uso de memoria y CPU
3. Considera usar `EXECUTION_MODE=once` para debugging

## 💰 **Optimización de Costos**

### **Para Minimizar Costos**

```env
EXECUTION_MODE=once
EXECUTION_INTERVAL_HOURS=168  # Una vez por semana
```

### **Para Máxima Actualización**

```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=6    # Cada 6 horas
```

## 🎯 **Casos de Uso Comunes**

### **Configuración Inicial**
```env
EXECUTION_MODE=once
```

### **Producción con Actualizaciones Diarias**
```env
EXECUTION_MODE=scheduled
EXECUTION_INTERVAL_HOURS=24
```

### **Desarrollo/Testing**
```env
EXECUTION_MODE=manual
```

---

**¡Tu microservicio está listo para procesar datos de Chesterton automáticamente! 🚀** 