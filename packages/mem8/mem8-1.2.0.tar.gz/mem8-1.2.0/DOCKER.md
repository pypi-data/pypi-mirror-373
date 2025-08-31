# AI-Mem Docker Setup

This document describes how to run AI-Mem using Docker for local development and production deployment.

## Quick Start

### Development Setup (Recommended)

For local development with hot reload and easier debugging:

```bash
# Start database services only
./scripts/dev-setup.sh

# Then run backend and frontend locally
cd backend && uv run python -m uvicorn aimem_api.main:app --reload --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

### Full Stack Deployment

For production-like deployment with all services in containers:

```bash
./scripts/deploy.sh
```

## Architecture

### Services

- **PostgreSQL**: Primary database (production-ready)
- **Redis**: Cache and session storage
- **Backend**: FastAPI application with automatic database migration
- **Frontend**: Next.js application with optimized production build

### Networking

All services run on a dedicated Docker network (`aimem-network`) for secure inter-service communication.

### Volumes

- `postgres_data`: Persistent PostgreSQL data
- `redis_data`: Persistent Redis data

## Configuration

### Environment Variables

The backend uses these key environment variables:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
REDIS_URL=redis://host:port
SECRET_KEY=your-secret-key-minimum-32-characters
DEBUG=false
```

### Development vs Production

| Environment | Database | Redis | Frontend | Backend |
|-------------|----------|-------|----------|---------|
| Development | postgres-dev:5433 | redis-dev:6380 | Local (npm) | Local (uv) |
| Production | postgres:5432 | redis:6379 | Container | Container |

## Commands

### Development

```bash
# Start infrastructure only
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop infrastructure
docker-compose -f docker-compose.dev.yml down

# Clean up volumes
docker-compose -f docker-compose.dev.yml down -v
```

### Production

```bash
# Start all services
docker-compose up -d

# Build and start (rebuild images)
docker-compose up --build -d

# View logs
docker-compose logs -f [service_name]

# Stop all services
docker-compose down

# Clean up everything including data
docker-compose down -v
```

## Health Checks

All services include health checks:

- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping` command  
- **Backend**: HTTP GET to `/api/v1/health`
- **Frontend**: HTTP GET to root path

## Troubleshooting

### Database Connection Issues

1. Ensure PostgreSQL is running: `docker-compose ps postgres`
2. Check logs: `docker-compose logs postgres`
3. Test connection: `docker-compose exec postgres psql -U aimem_user -d aimem`

### Backend Startup Issues

1. Check database connectivity
2. Verify environment variables: `docker-compose exec backend env | grep DATABASE_URL`
3. View backend logs: `docker-compose logs backend`

### Port Conflicts

If you get port binding errors:

- Development: Uses ports 5433 (PostgreSQL), 6380 (Redis)
- Production: Uses ports 5432 (PostgreSQL), 6379 (Redis), 8000 (Backend), 3000 (Frontend)

Stop conflicting services or change ports in docker-compose files.

## Orchestr8 Integration

This Docker setup is designed to be cloud-native and compatible with Orchestr8 deployment:

- All configuration via environment variables
- Health checks for Kubernetes liveness/readiness probes
- Multi-stage Dockerfiles for optimized production images
- Proper volume mounts for persistent data
- Network isolation for security

To deploy with Orchestr8:

1. Push images to your container registry
2. Update `docker-compose.yml` with your image tags
3. Configure environment variables for your cloud environment
4. Use Orchestr8 to deploy the compose file to Kubernetes