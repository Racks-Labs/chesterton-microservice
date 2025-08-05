#!/usr/bin/env python3
"""
Script de configuración para Railway.
Ejecuta el microservicio en modo único.
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
    """Función principal que ejecuta el microservicio."""
    
    logger.info("🚀 Iniciando Microservicio Chesterton")
    logger.info("📋 Modo: Ejecución única optimizada")
    
    # Ejecutar el script optimizado
    script_path = "scripts/run_once_optimized.py"
    
    try:
        result = subprocess.run([sys.executable, script_path])
        sys.exit(result.returncode)
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando {script_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 