.PHONY: help install dev test lint format clean build up down logs

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Backend commands
install: ## Install dependencies using uv
	uv sync

dev: ## Start development environment
	docker compose up --build

build: ## Build all containers
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Show logs for all services
	docker compose logs -f

# Backend specific commands
backend-install: ## Install backend dependencies
	uv sync

backend-dev: ## Run backend in development mode
	uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

backend-test: ## Run backend tests
	uv run pytest backend/tests/

backend-lint: ## Lint backend code
	uv run ruff check backend/
	uv run mypy backend/

backend-format: ## Format backend code
	uv run black backend/
	uv run isort backend/

# Frontend commands
frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-dev: ## Run frontend in development mode
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	cd frontend && npm run build

# Database commands
db-migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

db-reset: ## Reset database
	docker compose down -v
	docker compose up -d postgres
	sleep 5
	docker compose exec backend alembic upgrade head

# Cleanup commands
clean: ## Clean up containers and volumes
	docker compose down -v
	docker system prune -f

clean-all: ## Clean up everything including images
	docker compose down -v --rmi all
	docker system prune -af

# Production commands
prod-build: ## Build for production
	docker compose -f docker-compose.prod.yml build

prod-up: ## Start production environment
	docker compose -f docker-compose.prod.yml up -d

# Health checks
health: ## Check health of all services
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/api/v1/health || echo "Backend not healthy"
	@echo "Checking frontend health..."
	@curl -f http://localhost:3000 || echo "Frontend not healthy"
