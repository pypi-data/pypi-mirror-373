#!/bin/bash
# AI-Mem Production Deployment Script

set -e

echo "🚀 Deploying AI-Mem full stack..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start all services
echo "🏗️  Building and starting all services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Wait for PostgreSQL
timeout 60s bash -c 'until docker-compose exec postgres pg_isready -U aimem_user -d aimem; do sleep 2; done'
echo "✅ PostgreSQL ready"

# Wait for backend
timeout 60s bash -c 'until curl -f http://localhost:8000/api/v1/health >/dev/null 2>&1; do sleep 2; done'
echo "✅ Backend ready"

# Wait for frontend
timeout 60s bash -c 'until curl -f http://localhost:3000 >/dev/null 2>&1; do sleep 2; done'
echo "✅ Frontend ready"

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "🌐 Services available at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "🔍 To view logs:"
echo "  docker-compose logs -f [service_name]"
echo ""
echo "🛑 To stop all services:"
echo "  docker-compose down"
echo ""
echo "🗑️  To clean up (including volumes):"
echo "  docker-compose down -v"