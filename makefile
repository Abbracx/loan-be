build:
	docker compose -f docker-compose.yml up --build -d --remove-orphans

up:
	docker compose -f docker-compose.yml up -d  --remove-orphans	

down:
	docker compose -f docker-compose.yml down

exec:
	docker compose -f docker-compose.yml exec -it web /bin/bash

# To check if the env variables has been loaded correctly!
config:
	docker compose -f docker-compose.yml config 

show-logs:
	docker compose -f docker-compose.yml logs

show-logs-db:
	docker compose -f docker-compose.yml logs postgres

show-logs-web:
	docker compose -f docker-compose.yml logs web

migrations:
	docker compose -f docker-compose.yml run --rm web python manage.py makemigrations

migrate:
	docker compose -f docker-compose.yml run --rm web python manage.py migrate

collectstatic:
	docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --no-input --clear

superuser:
	docker compose -f docker-compose.yml run --rm web python manage.py createsuperuser

down-v:
	docker compose -f docker-compose.yml down -v

volume:
	docker volume inspect local_postgres_data

loan-be-db:
	docker compose -f docker-compose.yml exec postgres psql --username=postgres --dbname=loan-be-db

flake8:
	docker compose -f docker-compose.yml exec web flake8 .

black-check:
	docker compose -f docker-compose.yml exec web black --check --exclude=migrations --exclude=venv .

black-diff:
	docker compose -f docker-compose.yml exec web black --diff --exclude=migrations --exclude=venv .

black:
	docker compose -f docker-compose.yml exec web black --exclude=migrations --exclude=venv .

isort-check:
	docker compose -f docker-compose.yml exec web isort . --check-only --skip venv --skip migrations

isort-diff:
	docker compose -f docker-compose.yml exec web isort . --diff --skip venv --skip migrations

isort:
	docker compose -f docker-compose.yml exec web isort . --skip venv --skip migrations

# Run tests with coverage
cov:
	docker compose -f docker-compose.yml exec web pytest tests/ -p no:warnings --ds=loan_be.settings.test --cov=. -vv

cov-html:
	docker compose -f docker-compose.yml exec web pytest tests/ -p no:warnings --ds=loan_be.settings.test --cov=. --cov-report html

test:
	docker compose -f docker-compose.yml exec web pytest -p no:warnings -v

test-print-logs:
	docker compose -f docker-compose.yml exec web pytest tests/ -p no:warnings --ds=loan_be.settings.test -vv -s

# API Tests 
install-newman:
	@echo "Installing Newman and dependencies..."
	yarn install

test-api-local:
	@echo "Running API tests against local environment..."
	yarn test:api:local

test-api-docker:
	@echo "Running API tests against Docker environment..."
	yarn test:api:docker

test-api-ci:
	@echo "Running API tests for CI..."
	yarn test:api:ci

# Local CI/CD Simulation
ci-local:
	@echo "Running local CI/CD simulation..."
	./scripts/local-ci.sh

ci-test:
	@echo "Running tests only..."
	python -m pytest tests/ --ds=loan_be.settings.test -v --cov=apps

ci-api-test:
	@echo "Running API tests..."
	npm install
	npm run test:api:docker

superuser-auto:
	@echo "Creating superuser automatically..."
	docker-compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@example.com').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')"

# Run Act (GitHub Actions locally)
act-test:
	@echo "Running GitHub Actions locally with Act..."
	act -j test

act-full:
	@echo "Running full GitHub Actions workflow locally..."
	act

