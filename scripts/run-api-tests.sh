#!/bin/bash
set -e

ENVIRONMENT=${1:-docker}

echo "Running API tests against $ENVIRONMENT environment..."

case $ENVIRONMENT in
  "development")
    yarn run test:api:dev
    ;;
  "docker")
    yarn run test:api:docker
    ;;
  "ci")
    yarn run test:api:ci
    ;;
  *)
    echo "Usage: $0 [development|docker|ci]"
    exit 1
    ;;
esac

echo "API tests completed!"
