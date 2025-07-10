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

# Local CI/CD Simulation
ci-local:
	@echo "Running local CI/CD simulation..."
	./scripts/local-ci.sh

ci-test:
	@echo "Running tests only..."
	python -m pytest tests/ --ds=loan_be.settings.test -v --cov=apps

# API Tests 
install-newman:
	@echo "Installing Newman and dependencies..."
	cd api-tests && yarn install

test-api-docker:
	@echo "Running API tests against Docker environment..."
	cd api-tests && yarn test:api:docker

test-api-ci:
	@echo "Running API tests for CI..."
	cd api-tests && yarn test:api:ci

ci-api-test:
	@echo "Running API tests..."
	cd api-tests && yarn install
	cd api-tests && yarn test:api:docker

test-integration:
	@echo "Running integration tests..."
	cd api-tests && yarn test:integration

test-smoke:
	@echo "Running smoke tests..."
	cd api-tests && yarn test:smoke

test-auth-flow:
	@echo "Running authentication flow tests..."
	cd api-tests && yarn test:auth

test-loan-flow:
	@echo "Running loan application flow tests..."
	cd api-tests && yarn test:loans

test-security:
	@echo "Running security tests..."
	cd api-tests && yarn test:security

superuser-auto:
	@echo "Creating superuser automatically..."
	docker compose -f docker-compose.yml exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@example.com').exists() or User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass123', first_name='Admin', last_name='User')"

# Run Act (GitHub Actions locally)
act-test:
	@echo "Running GitHub Actions locally with Act..."
	act -j test

act-full:
	@echo "Running full GitHub Actions workflow locally..."
	act