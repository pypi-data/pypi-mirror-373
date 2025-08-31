.PHONY: help install dev test lint format migrate upgrade seed clean

help: ## Show this help message
	@echo 'usage: make [target]'
	@echo ''
	@echo 'targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint: ## Run linting
	ruff check .
	mypy app/

format: ## Format code
	black .
	isort .

migrate: ## Create migration
	alembic revision --autogenerate -m "$(message)"

upgrade: ## Run migrations
	alembic upgrade head

seed: ## Seed database with initial data
	python -c "from app.db.init_db import init_db; init_db()"

clean: ## Clean up cache and temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop services with Docker Compose
	docker-compose down

docker-build: ## Build Docker image
	docker build -t fastapi-fullstack .

docker-logs: ## View Docker logs
	docker-compose logs -f