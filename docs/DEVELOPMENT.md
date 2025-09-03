# Sleepr Development Guide

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Analytics Engine](#analytics-engine)
- [Database Schema](#database-schema)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)

## 🎯 Project Overview

Sleepr is a comprehensive Fantasy Football management application designed to help you dominate your Sleeper leagues through advanced analytics and automation.

### Key Features
- **Multi-League Management**: Sync and manage multiple Sleeper teams
- **Dynasty Analytics**: Long-term asset valuation and strategy
- **ML-Powered Predictions**: Player performance forecasting
- **Trade Analysis**: AI-driven trade recommendations
- **Waiver Wire Intelligence**: Identify breakout candidates
- **Lineup Optimization**: Maximize your weekly scoring potential

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Go API        │    │   Python        │
│   (Future)      │◄──►│   Server        │◄──►│   Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   ML Models     │
                       │   Database      │    │   & Cache       │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Sleeper API   │
                       └─────────────────┘
```

### Technology Stack
- **Backend**: Go (Gin framework)
- **Analytics**: Python (FastAPI, scikit-learn, TensorFlow)
- **Database**: PostgreSQL with JSON support
- **External APIs**: Sleeper Fantasy Football API
- **Containerization**: Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites
- Go 1.21+
- Python 3.9+
- PostgreSQL 14+
- Git

### Quick Setup
```bash
# Clone and setup
git clone <your-repo-url>
cd Sleepr
make setup

# Start services
make run-all
```

### Manual Setup
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your settings

# 2. Install Go dependencies
cd api && go mod tidy

# 3. Setup Python environment
cd ../analytics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Setup database
createdb sleepr
make db-migrate
make db-seed
```

## 📚 API Documentation

### Core Endpoints

#### User Management
```
POST /api/v1/users          - Create user
GET  /api/v1/users/:id      - Get user details
```

#### Team Management
```
GET  /api/v1/teams          - List all teams
GET  /api/v1/teams/:id      - Get team details
POST /api/v1/teams/:id/sync - Sync from Sleeper
```

#### Player Data
```
GET /api/v1/players         - List players
GET /api/v1/players/:id     - Player details
GET /api/v1/players/:id/stats - Player statistics
```

#### Analytics
```
GET /api/v1/analytics/teams/:id/recommendations  - Team recommendations
GET /api/v1/analytics/players/:id/projection     - Player projections
GET /api/v1/analytics/waiver-wire                - Waiver wire targets
```

### Example API Calls

```bash
# Get team recommendations
curl http://localhost:8080/api/v1/analytics/teams/1/recommendations

# Get player projection
curl http://localhost:8080/api/v1/analytics/players/123/projection

# Sync team from Sleeper
curl -X POST http://localhost:8080/api/v1/teams/team123/sync
```

## 🧠 Analytics Engine

The Python analytics engine provides machine learning capabilities:

### Core Models
- **Performance Prediction**: Random Forest model for fantasy points
- **Opportunity Detection**: Waiver wire target identification
- **Trade Analysis**: Player value assessment
- **Lineup Optimization**: Mathematical optimization

### Analytics API (Port 8000)
```bash
# Player projection
POST /analytics/player-projection
{
  "player_id": 123,
  "weeks_back": 8
}

# Waiver wire recommendations
POST /analytics/waiver-wire
{
  "league_id": "league123",
  "position": "RB",
  "max_results": 10
}
```

### Model Training
```python
from analytics import SleeprAnalytics
from models import PlayerPerformanceModel

# Initialize and train model
analytics = SleeprAnalytics()
model = PlayerPerformanceModel()

# Train on historical data
training_data = analytics.get_training_data()
model.train(training_data)
model.save_model('models/player_performance.pkl')
```

## 🗄 Database Schema

### Core Tables
- **users**: User accounts and Sleeper integration
- **leagues**: League information and settings
- **teams**: Fantasy teams and rosters
- **players**: NFL player database
- **player_stats**: Historical performance data
- **roster_players**: Team rosters and positions

### Key Relationships
```sql
users (1) → (many) teams
teams (many) ← → (many) players (via roster_players)
players (1) → (many) player_stats
```

### Sample Queries
```sql
-- Get team roster with player details
SELECT p.name, p.position, rp.is_starter
FROM roster_players rp
JOIN players p ON rp.player_id = p.id
WHERE rp.team_id = 1;

-- Player performance trend
SELECT week, fantasy_points
FROM player_stats
WHERE player_id = 123 AND season = 2024
ORDER BY week;
```

## 🔄 Development Workflow

### Daily Development
```bash
# Start development environment
make watch-api     # API with hot reload
make run-analytics # Analytics service

# Run tests
make test

# Format code
make format && make lint
```

### Adding New Features
1. Update database schema (if needed)
2. Add Go API endpoints
3. Implement analytics logic (if needed)
4. Add tests
5. Update documentation

### Database Changes
```bash
# Create new migration
mkdir database/migrations/002_new_feature
# Add .up.sql and .down.sql files

# Apply migration
make db-migrate
```

## 🧪 Testing

### Go API Tests
```bash
cd api
go test ./... -v
```

### Python Analytics Tests
```bash
cd analytics
source venv/bin/activate
python -m pytest tests/ -v
```

### Integration Tests
```bash
# Start services
make run-all

# Run integration tests
make test-integration
```

## 🚢 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale analytics=2
```

### Production Environment
1. Set production environment variables
2. Use external PostgreSQL service
3. Configure reverse proxy (nginx)
4. Set up monitoring and logging
5. Configure backup strategy

### Environment Variables
```bash
# Production .env
DATABASE_URL=postgresql://user:pass@prod-db:5432/sleepr
ENVIRONMENT=production
JWT_SECRET=secure-random-key
SLEEPER_API_BASE_URL=https://api.sleeper.app/v1
```

## 📊 Monitoring & Logging

### Health Checks
- API: `GET /health`
- Analytics: `GET /health`
- Database: Connection monitoring

### Metrics to Track
- API response times
- Model prediction accuracy
- Database query performance
- Sleeper API rate limits

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run tests: `make test`
5. Commit changes: `git commit -am 'Add new feature'`
6. Push to branch: `git push origin feature/new-feature`
7. Submit pull request

## 📞 Support

For questions or issues:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Include logs and error messages
4. Specify environment details

## 📄 License

MIT License - see LICENSE file for details
