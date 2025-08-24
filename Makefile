.PHONY: help dev build up down logs migrate makemigrations superuser shell test lint fmt clean install

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment
	docker-compose up --build

build: ## Build Docker images
	docker-compose build

up: ## Start services in background
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

migrate: ## Run database migrations
	docker-compose exec web python manage.py migrate

makemigrations: ## Create new database migrations
	docker-compose exec web python manage.py makemigrations

superuser: ## Create Django superuser
	docker-compose exec web python manage.py createsuperuser

shell: ## Start Django shell
	docker-compose exec web python manage.py shell

test: ## Run tests with coverage
	docker-compose exec web pytest --cov=backend --cov-report=term-missing

test-watch: ## Run tests in watch mode
	docker-compose exec web ptw --runner "pytest --cov=backend --cov-report=term-missing"

lint: ## Run linting checks
	docker-compose exec web ruff check .
	docker-compose exec web black --check .
	docker-compose exec web mypy .

fmt: ## Format code
	docker-compose exec web ruff check . --fix
	docker-compose exec web black .

clean: ## Clean up containers and volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

install: ## Install dependencies locally
	pip install -e .[dev]

load-fixtures: ## Load test fixtures
	docker-compose exec web python manage.py loaddata fixtures/sites.json
	docker-compose exec web python manage.py loaddata fixtures/users.json

collectstatic: ## Collect static files
	docker-compose exec web python manage.py collectstatic --noinput

backup-db: ## Backup database
	docker-compose exec db pg_dump -U postgres pharma_drf > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database (usage: make restore-db FILE=backup.sql)
	docker-compose exec -T db psql -U postgres pharma_drf < $(FILE)

# Local development (without Docker)
dev-local: ## Start local development server
	python manage.py runserver

migrate-local: ## Run migrations locally
	python manage.py migrate

test-local: ## Run tests locally
	pytest --cov=backend --cov-report=term-missing

lint-local: ## Run linting locally
	ruff check .
	black --check .
	mypy .