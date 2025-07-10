#!/bin/bash
set -e

echo "🚀 Starting Local CI/CD Simulation..."

# Step 1: Setup environment
echo "📋 Setting up environment..."
cp .env.example .env
mkdir -p logs api-tests/newman-reports

# Step 2: Run unit tests
echo "🧪 Running Django unit tests..."
pytest tests/ --ds=loan_be.settings.test -v

# Step 3: Start Docker services
echo "🐳 Starting Docker services..."
make build

# Step 4: Wait for services
echo "⏳ Waiting for services to be ready..."
timeout 120 bash -c 'until curl -f http://0.0.0.0:8000/api/v1/auth/redoc/ 2>/dev/null; do echo "Waiting..."; sleep 5; done'

# Step 5: Create test data
echo "👤 Creating superuser..."
make superuser-auto

# Step 6: Run API tests
echo "🔍 Running API tests..."
yarn install
yarn test:api:docker

if [ $? -ne 0 ]; then
    echo "❌ API tests failed!"
    exit 1
fi
echo "✅ API tests passed!"

# Step 7: Generate reports
echo "📊 Generating reports..."
echo "✅ Local CI/CD simulation completed!"
echo "📁 Reports available in: api-tests/newman-reports/"
