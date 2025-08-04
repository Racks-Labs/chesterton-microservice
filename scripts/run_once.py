#!/usr/bin/env python3
"""
Script para ejecutar el microservicio una sola vez.
Ideal para Railway o ejecución manual.
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
    logger.info(f"📋 Script: {script_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=True,
            text=True,
            cwd="/app"
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} completado exitosamente")
            if result.stdout:
                logger.info(f"📤 Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ {description} falló")
            logger.error(f"📤 Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error ejecutando {script_name}: {e}")
        return False

def main():
    """Función principal que ejecuta todos los scripts en secuencia."""
    logger.info("🚀 Iniciando Microservicio Chesterton (Ejecución Única)")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Verificar variables de entorno críticas
    required_vars = ["GOOGLE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        logger.error("💡 Configura estas variables en Railway Dashboard")
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
    logger.info("🎉 Proceso completado")
    logger.info(f"📊 Resumen: {success_count}/{total_scripts} scripts ejecutados exitosamente")
    
    if success_count == total_scripts:
        logger.info("✅ Todos los scripts se ejecutaron correctamente")
        sys.exit(0)
    else:
        logger.warning(f"⚠️ {total_scripts - success_count} scripts fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main() 