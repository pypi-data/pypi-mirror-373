#!/bin/bash
# mem8 Development Setup Script

set -e

echo "🚀 Setting up mem8 development environment..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env (please review and update if needed)"
fi

# Start PostgreSQL and Redis for development
echo "🐳 Starting PostgreSQL and Redis containers..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout 60s bash -c 'until docker-compose -f docker-compose.dev.yml exec postgres-dev pg_isready -U dev_user -d mem8_dev; do sleep 2; done'

# Update .env for development database
echo "🔧 Configuring development database..."
if ! grep -q "DATABASE_URL.*5433" backend/.env; then
    sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://dev_user:dev_password@localhost:5433/mem8_dev|' backend/.env
fi
if ! grep -q "REDIS_URL.*6380" backend/.env; then
    sed -i 's|REDIS_URL=.*|REDIS_URL=redis://localhost:6380|' backend/.env
fi

echo "✅ Development environment ready!"
echo ""
echo "🔍 Services running:"
echo "  - PostgreSQL: localhost:5433"
echo "  - Redis: localhost:6380"
echo ""
echo "🚀 To start the applications:"
echo "  Backend:  cd backend && uv run python -m uvicorn mem8_api.main:app --reload --host 127.0.0.1 --port 8000"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "🔧 To view logs:"
echo "  docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo "🛑 To stop services:"
echo "  docker-compose -f docker-compose.dev.yml down"