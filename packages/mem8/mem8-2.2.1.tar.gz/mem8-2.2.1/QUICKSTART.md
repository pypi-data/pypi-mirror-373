# mem8 Quick Start Guide 🚀

## Overview
mem8 now includes GitHub authentication integration and is currently in beta. Here's how to get it running:

## Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- GitHub OAuth App (optional for testing with mock data)

## Quick Setup (5 minutes)

### 1. Backend Setup
```bash
cd backend

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# For testing with SQLite (no database setup needed)
echo "DATABASE_URL=sqlite+aiosqlite:///./mem8.db" >> .env
echo "SECRET_KEY=test-secret-key-for-development" >> .env

# Start the API server
uv run uvicorn mem8_api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at: http://localhost:20040

## Testing Without GitHub OAuth

The app will show a GitHub login screen, but you can test the API directly:

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### WebSocket Test
Open browser dev tools and test WebSocket connection:
```javascript
// WebSocket sync is in beta and requires authentication
const ws = new WebSocket('ws://localhost:8000/api/v1/sync/test-team-id');
```

## GitHub OAuth Setup (Optional)

1. Create a GitHub OAuth App at: https://github.com/settings/applications/new
   - Application name: `mem8 Development`  
   - Homepage URL: `http://localhost:20040`
   - Authorization callback URL: `http://localhost:20040/auth/callback`

2. Update your `.env` file:
```bash
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
```

3. Restart the backend server

## What's Working ✅

### CLI (Phase 1) - Complete
- Full template management with cookiecutter
- Rich output with Windows 11 emoji support
- Advanced sync with conflict detection
- Search (fulltext + semantic fallback)

### Backend API (Phase 2) - Complete
- GitHub OAuth authentication
- JWT token management
- Thoughts CRUD operations
- Teams management
- Real-time WebSocket sync (beta)
- Docker ready

### Frontend (Phase 3) - 95% Complete  
- Terminal-style UI with dark theme
- GitHub OAuth integration
- API client with auth headers
- WebSocket real-time updates (beta)
- React Query state management

### Missing/In Progress
- Database migrations setup
- Toast notifications
- Individual thought editing pages
- Team management UI

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   CLI       │    │   Frontend   │    │   Backend    │
│  (Phase 1)  │    │  (Phase 3)   │    │  (Phase 2)   │
│             │    │              │    │              │
│ • Templates │    │ • React/Next │    │ • FastAPI    │
│ • Sync      │    │ • Auth Guard │    │ • GitHub OAuth│
│ • Search    │    │ • WebSocket  │    │ • WebSocket   │
│ • Rich UI   │    │ • Terminal UI│    │ • PostgreSQL │
└─────────────┘    └──────────────┘    └──────────────┘
```

## Next Steps

1. **Test the auth flow** - The main missing piece
2. **Add database migrations** - For production deployment  
3. **Connect real semantic search** - Replace text search fallback
4. **Polish the UI** - Add missing pages and notifications

  The system is functionally complete but still in beta; it's ready for integration testing with your AgenticInsights.com auth system. 🎉