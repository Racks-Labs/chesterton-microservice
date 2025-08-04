#!/usr/bin/env python3
"""
Script optimizado para cron jobs semanales.
Se ejecuta, procesa los datos y termina.
Ideal para Railway cron jobs.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

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

def main():
    """Función principal optimizada para cron jobs."""
    start_time = datetime.now()
    
    logger.info("🚀 Iniciando Cron Job Semanal - Microservicio Chesterton")
    logger.info(f"⏰ Inicio: {start_time.isoformat()}")
    
    # Verificar variables de entorno críticas
    required_vars = ["GOOGLE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        sys.exit(1)
    
    logger.info("✅ Variables de entorno verificadas")
    
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
    
    logger.info("🎉 Cron Job Semanal Completado")
    logger.info(f"⏰ Duración total: {duration}")
    logger.info(f"📊 Resumen: {success_count}/{total_scripts} scripts ejecutados exitosamente")
    
    if success_count == total_scripts:
        logger.info("✅ Todos los scripts se ejecutaron correctamente")
        sys.exit(0)
    else:
        logger.warning(f"⚠️ {total_scripts - success_count} scripts fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main() 