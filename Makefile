.PHONY: setup build run stop logs clean help

# Variables
SERVICE_NAME = chesterton-microservice
COMPOSE_FILE = docker-compose.yml

# Comandos principales
setup: ## Configurar el entorno inicial
	@echo "🔧 Configurando microservicio..."
	@./setup.sh

build: ## Construir la imagen Docker
	@echo "🔨 Construyendo imagen Docker..."
	@docker-compose build

run: ## Ejecutar el microservicio
	@echo "🚀 Ejecutando microservicio..."
	@./run.sh

stop: ## Detener el microservicio
	@echo "🛑 Deteniendo microservicio..."
	@docker-compose down

logs: ## Ver logs del microservicio
	@echo "📋 Mostrando logs..."
	@docker-compose logs -f

clean: ## Limpiar contenedores e imágenes
	@echo "🧹 Limpiando recursos Docker..."
	@docker-compose down --rmi all --volumes --remove-orphans
	@docker system prune -f

restart: stop run ## Reiniciar el microservicio

status: ## Ver estado del microservicio
	@echo "📊 Estado del microservicio:"
	@docker-compose ps

shell: ## Acceder al shell del contenedor
	@echo "🐚 Accediendo al shell del contenedor..."
	@docker-compose exec chesterton-microservice /bin/bash

test: ## Ejecutar tests (placeholder)
	@echo "🧪 Ejecutando tests..."
	@echo "Tests no implementados aún"

help: ## Mostrar esta ayuda
	@echo "📋 Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 Uso: make <comando>"
	@echo "   Ejemplo: make setup" 