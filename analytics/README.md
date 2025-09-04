# Sleepr Analytics System

Advanced machine learning and analytics engine for fantasy football dynasty management.

## Overview

The Sleepr Analytics System provides AI-powered insights, predictions, and recommendations to help fantasy football managers make data-driven decisions for their dynasty teams. Built with Python, FastAPI, and modern ML libraries.

## Features

### 🎯 Player Projections
- **Weekly/Season Projections**: ML-powered fantasy point predictions
- **Confidence Intervals**: Statistical uncertainty bounds for projections
- **Injury Risk Assessment**: Predictive injury risk modeling
- **Performance Trending**: Trend analysis for player performance
- **Multi-week Forecasting**: Projections for 1-16 weeks ahead

### 🔍 Waiver Wire Intelligence
- **AI Recommendations**: Smart pickup suggestions with 1-10 scoring
- **Position-Based Filtering**: Targeted recommendations by positional need
- **Ownership Analysis**: Low-ownership gems identification
- **Trending Players**: Rising/falling player identification
- **Budget Optimization**: FAAB budget allocation recommendations

### 🤝 Trade Analyzer
- **Multi-Player Trade Analysis**: Complex trade evaluation
- **Dynasty Value Assessment**: Long-term value implications
- **Risk/Reward Analysis**: Comprehensive risk assessment
- **Grade System**: A+ to F trade grading
- **Positional Impact**: How trades affect roster construction

### 💎 Dynasty Valuations
- **Current Value Calculations**: Real-time dynasty values
- **Future Projections**: 1-3 year value forecasts
- **Age Curve Analysis**: Position-specific aging patterns
- **Peak Performance Windows**: Optimal production years
- **Dynasty Tier Classifications**: Elite to Dart Throw rankings

### 📊 Team Analytics
- **Strength Analysis**: Positional strengths and weaknesses
- **Championship Odds**: Monte Carlo simulation for title chances
- **Draft Strategy**: Data-driven draft recommendations
- **Roster Construction**: Optimal lineup building advice

## Architecture

### API Layer (`/api/main.py`)
- **FastAPI Framework**: High-performance async API
- **RESTful Endpoints**: Clean, documented API design
- **CORS Support**: Frontend integration ready
- **Error Handling**: Robust error management
- **Health Monitoring**: Service health endpoints

### Machine Learning Models (`/api/models.py`)
- **PlayerProjectionModel**: Ensemble ML for fantasy projections
- **WaiverWireRecommendationModel**: Smart pickup recommendations
- **TradeAnalyzerModel**: Multi-factor trade evaluation
- **DynastyValueModel**: Long-term player valuations

### Data Processing (`/api/data_processor.py`)
- **Feature Engineering**: Advanced statistical features
- **Data Normalization**: Consistent data formatting
- **Age Curve Analysis**: Position-specific aging patterns
- **Performance Metrics**: Fantasy-relevant statistics

### External Integration (`/api/sleeper_client.py`)
- **Sleeper API Client**: Async API integration
- **Data Caching**: Performance optimization
- **Rate Limiting**: API quota management
- **Error Recovery**: Robust API error handling

## Technology Stack

### Core Framework
- **Python 3.9+**: Modern Python with async support
- **FastAPI**: High-performance web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production

### Machine Learning
- **scikit-learn**: Core ML algorithms
- **XGBoost**: Gradient boosting for predictions
- **TensorFlow**: Deep learning capabilities
- **pandas/numpy**: Data manipulation and analysis

### Data & Storage
- **PostgreSQL**: Primary data storage
- **Redis**: Caching and session management
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations

### External APIs
- **Sleeper API**: Fantasy football data source
- **aiohttp**: Async HTTP client
- **BeautifulSoup4**: Web scraping capabilities

## API Endpoints

### Player Projections
```http
POST /projections/player
Content-Type: application/json

{
    "player_id": "4046",
    "weeks_ahead": 4,
    "league_settings": {
        "scoring": "ppr"
    }
}
```

### Waiver Wire Recommendations
```http
POST /waiver-wire/recommendations
Content-Type: application/json

{
    "league_id": "123456789",
    "team_id": "1",
    "position_needs": ["RB", "WR"],
    "budget_constraint": 50.0
}
```

### Trade Analysis
```http
POST /trade/analyze
Content-Type: application/json

{
    "giving_players": ["4046", "5849"],
    "receiving_players": ["2133", "6794"],
    "league_id": "123456789",
    "team_id": "1"
}
```

### Dynasty Value
```http
POST /dynasty/value
Content-Type: application/json

{
    "player_id": "4046",
    "league_settings": {
        "type": "dynasty",
        "teams": 12
    }
}
```

### Team Insights
```http
GET /analytics/insights/{team_id}
```

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+

### Installation
```bash
cd analytics
pip install -r requirements.txt
```

### Environment Configuration
```bash
# Create .env file
POSTGRES_URL=postgresql://user:pass@localhost/sleepr
REDIS_URL=redis://localhost:6379
SLEEPER_API_BASE=https://api.sleeper.app/v1
LOG_LEVEL=INFO
```

### Database Setup
```bash
# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_data.py
```

### Running the Service
```bash
# Development
uvicorn api.main:app --reload --port 8001

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8001 --workers 4
```

## Model Training

### Data Collection
```bash
# Collect historical data
python scripts/collect_data.py --seasons 2020,2021,2022,2023,2024

# Update player database
python scripts/update_players.py
```

### Training Models
```bash
# Train projection model
python scripts/train_projections.py

# Train waiver wire model
python scripts/train_waiver.py

# Validate models
python scripts/validate_models.py
```

### Model Deployment
```bash
# Deploy trained models
python scripts/deploy_models.py --environment production
```

## Performance & Scaling

### Caching Strategy
- **Player Data**: 1-hour cache for static data
- **Projections**: 6-hour cache for predictions
- **Market Data**: 30-minute cache for trending info

### API Performance
- **Response Times**: < 200ms for cached requests
- **Throughput**: 1000+ requests/minute
- **Availability**: 99.9% uptime target

### Monitoring
- **Health Checks**: `/health` endpoint
- **Metrics**: Response times, error rates, cache hit ratios
- **Logging**: Structured JSON logging with correlation IDs

## Testing

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load/locustfile.py --host http://localhost:8001
```

## Data Sources

### Primary Sources
- **Sleeper API**: Real-time fantasy data
- **NFL Stats**: Official performance data
- **Injury Reports**: Injury status and history

### Enhanced Data
- **Weather Data**: Game condition impacts
- **Vegas Lines**: Betting market insights
- **Target Share**: Advanced receiving metrics
- **Snap Counts**: Usage rate analysis

## Machine Learning Details

### Feature Engineering
- **Player Features**: Age, experience, physical attributes
- **Performance Features**: Recent stats, trends, consistency
- **Situational Features**: Team, matchup, game script
- **Advanced Metrics**: Target share, air yards, red zone usage

### Model Architecture
- **Ensemble Methods**: Combining multiple algorithms
- **Feature Selection**: Automated feature importance
- **Cross-Validation**: Time-series aware validation
- **Hyperparameter Tuning**: Automated optimization

### Model Validation
- **Backtesting**: Historical performance validation
- **A/B Testing**: Live model comparison
- **Error Analysis**: Systematic error investigation
- **Drift Detection**: Model performance monitoring

## Contributing

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Code formatting
black analytics/
flake8 analytics/
```

### Testing Guidelines
- Write tests for all new features
- Maintain >90% code coverage
- Include integration tests for API endpoints
- Mock external API calls in tests

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Document all public methods
- Keep functions small and focused

## Deployment

### Docker
```bash
# Build image
docker build -t sleepr-analytics .

# Run container
docker run -p 8001:8001 sleepr-analytics
```

### Kubernetes
```yaml
# See deployment/kubernetes/analytics-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sleepr-analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sleepr-analytics
  template:
    metadata:
      labels:
        app: sleepr-analytics
    spec:
      containers:
      - name: analytics
        image: sleepr-analytics:latest
        ports:
        - containerPort: 8001
```

## Future Enhancements

### Advanced Analytics
- [ ] Deep learning for player projections
- [ ] Natural language processing for injury reports
- [ ] Computer vision for game film analysis
- [ ] Reinforcement learning for optimal lineups

### Data Expansion
- [ ] College football data integration
- [ ] Social media sentiment analysis
- [ ] Advanced tracking data (Next Gen Stats)
- [ ] Historical weather impact analysis

### Real-time Features
- [ ] Live game projections
- [ ] In-game lineup optimization
- [ ] Real-time trade alerts
- [ ] Push notification system

### User Experience
- [ ] Personalized recommendations
- [ ] Custom scoring systems
- [ ] Interactive visualizations
- [ ] Mobile app integration

## Support

For questions or issues:
- Check the API documentation at `/docs`
- Review logs for error details
- Monitor health endpoint for service status
- Contact the development team for complex issues
