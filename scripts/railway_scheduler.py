#!/usr/bin/env python3
"""
Script optimizado para Railway que ejecuta periódicamente.
Se ejecuta, procesa los datos, y luego se duerme hasta la próxima ejecución.
Ideal para Railway sin cron jobs nativos.
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """Ejecuta un script individual y maneja errores."""
    logger.info(f"🚀 Ejecutando: {description}")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=True,
            text=True,
            cwd="/app",
            timeout=1800  # 30 minutos máximo por script
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} completado exitosamente")
            return True
        else:
            logger.error(f"❌ {description} falló")
            logger.error(f"📤 Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {description} excedió el tiempo límite (30 min)")
        return False
    except Exception as e:
        logger.error(f"❌ Error ejecutando {script_name}: {e}")
        return False

def run_all_scripts():
    """Ejecuta todos los scripts en secuencia."""
    start_time = datetime.now()
    
    logger.info("🔄 Iniciando procesamiento de datos")
    logger.info(f"⏰ Inicio: {start_time.isoformat()}")
    
    # Lista de scripts a ejecutar en orden
    scripts_to_run = [
        ("faq_to_md.py", "Extracción de FAQs del PDF"),
        ("wp_chesterton.py", "Scraping de WordPress"),
        ("xml_to_db.py", "Procesamiento de XML y carga a base de datos"),
        ("chesterton_qdrant.py", "Indexación en Qdrant")
    ]
    
    success_count = 0
    total_scripts = len(scripts_to_run)
    
    for script_name, description in scripts_to_run:
        if run_script(script_name, description):
            success_count += 1
        else:
            logger.warning(f"⚠️ Continuando con el siguiente script...")
    
    # Resumen final
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("🎉 Procesamiento completado")
    logger.info(f"⏰ Duración total: {duration}")
    logger.info(f"📊 Resumen: {success_count}/{total_scripts} scripts ejecutados exitosamente")
    
    return success_count == total_scripts

def calculate_sleep_time():
    """Calcula cuánto tiempo dormir hasta la próxima ejecución."""
    # Obtener intervalo desde variables de entorno (en horas)
    interval_hours = int(os.getenv("EXECUTION_INTERVAL_HOURS", "168"))  # 7 días por defecto
    
    # Calcular próxima ejecución
    now = datetime.now()
    next_execution = now + timedelta(hours=interval_hours)
    
    logger.info(f"⏰ Próxima ejecución programada: {next_execution.isoformat()}")
    logger.info(f"😴 Durmiendo {interval_hours} horas ({interval_hours * 3600} segundos)")
    
    return interval_hours * 3600

def main():
    """Función principal optimizada para Railway."""
    logger.info("🚀 Iniciando Microservicio Chesterton (Modo Scheduler para Railway)")
    
    # Verificar variables de entorno críticas
    required_vars = ["GOOGLE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        logger.error("💡 Configura estas variables en Railway Dashboard")
        sys.exit(1)
    
    logger.info("✅ Variables de entorno verificadas")
    
    # Obtener configuración
    interval_hours = int(os.getenv("EXECUTION_INTERVAL_HOURS", "168"))  # 7 días
    logger.info(f"⏰ Configurado para ejecutar cada {interval_hours} horas")
    
    # Ejecutar inmediatamente la primera vez
    logger.info("🚀 Ejecutando primera vez inmediatamente...")
    run_all_scripts()
    
    # Bucle principal
    while True:
        try:
            # Calcular tiempo de sueño
            sleep_seconds = calculate_sleep_time()
            
            # Dormir hasta la próxima ejecución
            logger.info(f"😴 Durmiendo {sleep_seconds} segundos...")
            time.sleep(sleep_seconds)
            
            # Ejecutar procesamiento
            logger.info("🔄 Despertando para ejecutar procesamiento...")
            run_all_scripts()
            
        except KeyboardInterrupt:
            logger.info("🛑 Recibida señal de interrupción, terminando...")
            break
        except Exception as e:
            logger.error(f"❌ Error en el bucle principal: {e}")
            logger.info("🔄 Reintentando en 1 hora...")
            time.sleep(3600)  # Esperar 1 hora antes de reintentar

if __name__ == "__main__":
    main() 