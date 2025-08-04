#!/usr/bin/env python3
"""
Script de configuración para Railway.
Permite elegir entre diferentes modos de ejecución.
"""

import os
import sys
import subprocess
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal que determina el modo de ejecución."""
    
    # Obtener modo de ejecución desde variables de entorno
    execution_mode = os.getenv("EXECUTION_MODE", "once").lower()
    
    logger.info(f"🚀 Iniciando Microservicio Chesterton")
    logger.info(f"📋 Modo de ejecución: {execution_mode}")
    
    if execution_mode == "once":
        logger.info("🔄 Modo: Ejecución única")
        script_path = "scripts/run_once.py"
    elif execution_mode == "scheduled":
        logger.info("⏰ Modo: Ejecución programada")
        script_path = "scripts/scheduler.py"
    elif execution_mode == "cron":
        logger.info("⏰ Modo: Cron job optimizado")
        script_path = "scripts/cron_job.py"
    elif execution_mode == "manual":
        logger.info("👤 Modo: Manual (solo entrypoint.sh)")
        script_path = "entrypoint.sh"
    else:
        logger.error(f"❌ Modo de ejecución no válido: {execution_mode}")
        logger.info("💡 Modos disponibles: once, scheduled, cron, manual")
        sys.exit(1)
    
    # Ejecutar el script correspondiente
    try:
        if script_path.endswith(".py"):
            result = subprocess.run([sys.executable, script_path])
        else:
            result = subprocess.run([f"./{script_path}"], shell=True)
        
        sys.exit(result.returncode)
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando {script_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 