#!/bin/bash

# Script de entrada simplificado para el microservicio Chesterton
# Ejecuta el procesamiento una vez y termina

echo "🚀 Iniciando Microservicio Chesterton"
echo "📋 Modo: Ejecución única"

# Ejecutar el script optimizado
python scripts/run_once_optimized.py

# Salir con el código de estado del script
exit $? 