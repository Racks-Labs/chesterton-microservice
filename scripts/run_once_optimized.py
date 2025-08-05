#!/usr/bin/env python3
"""
Script optimizado para ejecución única en Railway.
Se ejecuta una vez, procesa todos los datos, y termina.
Ideal para cron externo o ejecución manual.
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
            if result.stdout.strip():
                logger.info(f"📤 Output: {result.stdout.strip()}")
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

def verify_environment():
    """Verifica que las variables de entorno críticas estén configuradas."""
    logger.info("🔍 Verificando variables de entorno...")
    
    required_vars = [
        "GOOGLE_API_KEY",
        "QDRANT_URL", 
        "QDRANT_API_KEY",
        "WORDPRESS_SITE_URL",
        "DB_URL",
        "XML_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"tu_{var.lower()}_aqui":
            missing_vars.append(var)
        else:
            logger.info(f"✅ {var}: Configurado")
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        logger.error("💡 Configura estas variables en Railway Dashboard")
        return False
    
    logger.info("✅ Todas las variables de entorno están configuradas")
    return True

def verify_pdf_exists():
    """Verifica que el archivo PDF existe."""
    pdf_path = "/app/data/faq_chesterton.pdf"
    if os.path.exists(pdf_path):
        logger.info(f"✅ PDF encontrado: {pdf_path}")
        return True
    else:
        logger.error(f"❌ PDF no encontrado: {pdf_path}")
        return False

def main():
    """Función principal para ejecución única."""
    start_time = datetime.now()
    
    logger.info("🚀 Iniciando Microservicio Chesterton (Ejecución Única)")
    logger.info(f"⏰ Inicio: {start_time.isoformat()}")
    
    # Verificar entorno
    if not verify_environment():
        logger.error("❌ Error en verificación de entorno. Terminando...")
        sys.exit(1)
    
    # Verificar PDF
    if not verify_pdf_exists():
        logger.error("❌ Error: PDF no encontrado. Terminando...")
        sys.exit(1)
    
    # Lista de scripts a ejecutar en orden
    scripts_to_run = [
        ("faq_to_md.py", "Extracción de FAQs del PDF"),
        ("wp_chesterton.py", "Scraping de WordPress"),
        ("xml_to_db.py", "Procesamiento de XML y carga a base de datos"),
        ("chesterton_qdrant.py", "Indexación en Qdrant")
    ]
    
    success_count = 0
    total_scripts = len(scripts_to_run)
    
    logger.info(f"📋 Ejecutando {total_scripts} scripts en secuencia...")
    
    for i, (script_name, description) in enumerate(scripts_to_run, 1):
        logger.info(f"📝 [{i}/{total_scripts}] {description}")
        
        if run_script(script_name, description):
            success_count += 1
        else:
            logger.warning(f"⚠️ Script falló, pero continuando...")
    
    # Resumen final
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("🎉 Procesamiento completado")
    logger.info(f"⏰ Duración total: {duration}")
    logger.info(f"📊 Resumen: {success_count}/{total_scripts} scripts ejecutados exitosamente")
    
    if success_count == total_scripts:
        logger.info("✅ Todos los scripts se ejecutaron exitosamente")
        logger.info("🔄 El servicio terminará ahora. Para volver a ejecutar, haz redeploy.")
        sys.exit(0)
    else:
        logger.warning(f"⚠️ {total_scripts - success_count} scripts fallaron")
        logger.info("🔄 El servicio terminará ahora. Revisa los logs para más detalles.")
        sys.exit(1)

if __name__ == "__main__":
    main() 