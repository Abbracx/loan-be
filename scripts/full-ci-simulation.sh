#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Cleanup function
cleanup() {
    log "Cleaning up..."
    make down-v 2>/dev/null || true
}
# Set trap for cleanup
trap cleanup EXIT

log "🚀 Starting Full CI/CD Simulation"

# Step 1: Environment setup
log "📋 Setting up environment..."
cp .env.example .env
mkdir -p logs api-tests/newman-reports

# Step 2: Lint and format check
log "🔍 Running code quality checks..."
if command -v black &> /dev/null; then
    black --check apps/ || warning "Code formatting issues found"
fi

if command -v isort &> /dev/null; then
    isort --check-only apps/ || warning "Import sorting issues found"
fi

if command -v flake8 &> /dev/null; then
    flake8 apps/ || warning "Flake8 issues found"
fi

# Step 3: Unit tests
log "🧪 Running Django unit tests..."
pytest tests/ --ds=loan_be.settings.test -v --cov=apps || error "Unit tests failed"
success "Unit tests passed"

# Step 4: Build and start services
log "🐳 Building and starting services..."
make build

# Step 5: Wait for services
log "⏳ Waiting for services..."
for i in {1..36}; do
    if curl -f http://localhost:8080/api/v1/auth/redoc/ 2>/dev/null; then
        echo "Services are ready!"
        break
    fi
    echo "Waiting... ($i/36)"
    sleep 5
done

# Create superuser
log "👤 Creating superuser..."
make superuser-auto || error "Failed to create superuser"

# API tests
log "🔍 Running API tests..."
cd api-tests && yarn install || error "Failed to install Newman"
cd api-tests && yarn test:api:docker || error "API tests failed"
success "API tests passed"

success "🎉 Full CI/CD simulation completed!"
log "📁 Reports: api-tests/newman-reports/"
log "🌐 API: http://localhost:8080"
log "🌐 Admin: http://localhost:8080/admin"
log "📖 Documentation: http://localhost:8080/api/v1/auth/redoc/"