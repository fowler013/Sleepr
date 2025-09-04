# Sleepr Deployment Configuration

Comprehensive deployment solution for the Sleepr fantasy football management application, supporting Docker, Kubernetes, and local development environments.

## Overview

This deployment system provides automated, scalable, and production-ready deployment options for the complete Sleepr stack including:

- **Go API Backend** - Fantasy football data management
- **Python Analytics Engine** - ML-powered insights and recommendations
- **React Frontend** - Modern web interface
- **PostgreSQL Database** - Primary data storage
- **Redis Cache** - Performance optimization
- **Nginx Reverse Proxy** - Load balancing and SSL termination
- **Monitoring Stack** - Prometheus and Grafana

## Deployment Options

### 🐳 Docker Compose (Recommended for Development/Testing)
- **Single-command deployment** with `docker-compose`
- **Isolated services** with networking and volume management
- **Health checks** and automatic restarts
- **Local development** with hot-reload support

### ☸️ Kubernetes (Recommended for Production)
- **Horizontal Pod Autoscaling** for dynamic scaling
- **Rolling deployments** with zero downtime
- **Persistent storage** with automatic backups
- **SSL/TLS termination** with Let's Encrypt
- **Resource limits** and quality of service

### 💻 Local Development
- **Native development** environment
- **Hot reload** for all services
- **Database containers** with local application servers
- **Easy debugging** and development workflow

## Quick Start

### Prerequisites
```bash
# For Docker deployment
docker --version
docker-compose --version

# For Kubernetes deployment
kubectl version
helm version  # optional but recommended

# For local development
go version
node --version
python3 --version
```

### One-Command Deployment

```bash
# Docker development environment
./deployment/deploy.sh docker development

# Kubernetes production environment
./deployment/deploy.sh kubernetes production

# Local development setup
./deployment/deploy.sh local development
```

## Docker Compose Deployment

### Development Environment
```bash
# Deploy complete stack
./deployment/deploy.sh docker development

# Access applications
# Frontend: http://localhost:3000
# API: http://localhost:8080
# Analytics: http://localhost:8001
# Grafana: http://localhost:3001
```

### Production Environment
```bash
# Set production environment
./deployment/deploy.sh docker production

# With SSL certificates
cp your-ssl-cert.crt deployment/nginx/ssl/sleepr.crt
cp your-ssl-key.key deployment/nginx/ssl/sleepr.key
```

### Services Overview
| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React web application |
| API | 8080 | Go backend service |
| Analytics | 8001 | Python ML service |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache and sessions |
| Nginx | 80/443 | Reverse proxy |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Monitoring dashboard |

## Kubernetes Deployment

### Cluster Setup
```bash
# Create namespace
kubectl create namespace sleepr

# Deploy application
kubectl apply -f deployment/kubernetes/sleepr-deployment.yaml

# Check deployment status
kubectl get pods -n sleepr
kubectl get services -n sleepr
```

### Features
- **3 API replicas** with load balancing
- **2 Analytics replicas** for ML workloads
- **2 Frontend replicas** for high availability
- **Horizontal Pod Autoscaling** based on CPU/memory
- **Persistent volumes** for database storage
- **Ingress controller** with SSL termination
- **Health checks** and readiness probes

### Scaling
```bash
# Manual scaling
kubectl scale deployment sleepr-api --replicas=5 -n sleepr

# Auto-scaling is configured for:
# - API: 3-10 replicas based on 70% CPU
# - Analytics: 2-8 replicas based on 75% CPU
```

### SSL/TLS Configuration
```yaml
# Ingress with Let's Encrypt
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - sleepr.example.com
    secretName: sleepr-tls
```

## Local Development

### Setup
```bash
# Start local environment
./deployment/deploy.sh local development

# Services will start on:
# Frontend: http://localhost:3000
# API: http://localhost:8080  
# Analytics: http://localhost:8001
```

### Development Workflow
```bash
# Start databases only
docker-compose -f deployment/docker-compose.yml up -d postgres redis

# Run services natively for development
cd api && go run cmd/server/main.go
cd analytics && uvicorn api.main:app --reload --port 8001
cd web/frontend && npm start
```

### Hot Reload
- **Go API**: Automatic rebuild on file changes
- **Python Analytics**: Uvicorn auto-reload
- **React Frontend**: Webpack dev server hot reload

## Configuration

### Environment Variables
```bash
# Database
POSTGRES_PASSWORD=secure_password
POSTGRES_USER=sleepr_user
POSTGRES_DB=sleepr

# Redis
REDIS_PASSWORD=redis_password

# JWT Authentication
JWT_SECRET=your_jwt_secret_key

# API URLs
API_URL=http://localhost:8080
ANALYTICS_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000

# Monitoring
GRAFANA_PASSWORD=grafana_admin_password
```

### Custom Configuration
```bash
# Create environment-specific config
cp .env.example .env.production
# Edit configuration
vim .env.production
```

## Monitoring & Observability

### Prometheus Metrics
- **Application metrics** from all services
- **Infrastructure metrics** (CPU, memory, disk)
- **Custom business metrics** for fantasy football insights
- **SLI/SLO monitoring** for service reliability

### Grafana Dashboards
- **Application Performance** dashboard
- **Infrastructure Monitoring** dashboard  
- **Fantasy Football Metrics** dashboard
- **Error Rate and Latency** monitoring

### Health Checks
```bash
# Check service health
curl http://localhost:8080/api/v1/health
curl http://localhost:8001/health
curl http://localhost:3000

# Docker health status
docker-compose ps

# Kubernetes health status
kubectl get pods -n sleepr
```

## Security

### Network Security
- **Internal networking** isolates services
- **Nginx reverse proxy** with rate limiting
- **SSL/TLS encryption** for all external traffic
- **Security headers** for web protection

### Authentication & Authorization
- **JWT token authentication** with secure secrets
- **API rate limiting** to prevent abuse
- **CORS configuration** for frontend security
- **Database connection encryption**

### Secrets Management
```bash
# Kubernetes secrets
kubectl create secret generic sleepr-secrets \
  --from-env-file=.env.production \
  --namespace=sleepr

# Docker secrets (using .env file)
# Environment variables are automatically loaded
```

## Backup & Recovery

### Database Backups
```bash
# Automated daily backups
docker exec sleepr-postgres pg_dump -U sleepr_user sleepr > backup_$(date +%Y%m%d).sql

# Kubernetes backup with persistent volumes
kubectl exec -n sleepr postgres-0 -- pg_dump -U sleepr_user sleepr > backup.sql
```

### Disaster Recovery
- **Database replication** for high availability
- **Persistent volume snapshots** for data recovery
- **Multi-region deployment** for disaster recovery
- **Automated backup verification** and restore testing

## Performance Optimization

### Caching Strategy
- **Redis caching** for frequently accessed data
- **Application-level caching** in Go and Python
- **CDN integration** for static assets
- **Database query optimization** with indexes

### Load Balancing
- **Nginx upstream** load balancing
- **Kubernetes service** load balancing
- **Database connection pooling**
- **Analytics request queuing**

### Resource Limits
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## CI/CD Integration

### GitHub Actions
```yaml
# Automated deployment pipeline
- Build and test applications
- Build Docker images
- Deploy to staging environment
- Run integration tests
- Deploy to production (manual approval)
```

### Deployment Pipeline
1. **Code commit** triggers pipeline
2. **Automated testing** (unit, integration)
3. **Docker image builds** with versioning
4. **Staging deployment** for validation
5. **Production deployment** with approval
6. **Health monitoring** and rollback capability

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs [service_name]
kubectl logs -f deployment/[service_name] -n sleepr

# Check health
curl -f http://localhost:8080/api/v1/health
```

#### Database Connection Issues
```bash
# Test database connectivity
docker exec -it sleepr-postgres psql -U sleepr_user -d sleepr

# Check environment variables
docker exec sleepr-api env | grep DATABASE
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats
kubectl top pods -n sleepr

# Check application metrics
curl http://localhost:9090/metrics
```

### Debugging Commands
```bash
# Docker debugging
docker-compose logs -f [service]
docker exec -it [container] /bin/bash

# Kubernetes debugging  
kubectl describe pod [pod-name] -n sleepr
kubectl logs -f [pod-name] -n sleepr
kubectl exec -it [pod-name] -n sleepr -- /bin/bash
```

## Scaling Guide

### Horizontal Scaling
```bash
# Docker Compose scaling
docker-compose up -d --scale api=3 --scale analytics=2

# Kubernetes scaling
kubectl scale deployment sleepr-api --replicas=5 -n sleepr
```

### Vertical Scaling
```yaml
# Increase resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Database Scaling
- **Read replicas** for query performance
- **Connection pooling** for concurrent connections
- **Sharding strategies** for large datasets
- **Caching layers** for hot data

## Maintenance

### Updates and Upgrades
```bash
# Update application
./deployment/deploy.sh docker production

# Rolling update in Kubernetes
kubectl set image deployment/sleepr-api api=sleepr-api:v2.0.0 -n sleepr
```

### Log Management
- **Centralized logging** with ELK stack
- **Log rotation** to prevent disk issues
- **Structured logging** for better analysis
- **Log retention policies** for compliance

### Monitoring Alerts
- **High error rates** alert configuration
- **Performance degradation** notifications
- **Resource exhaustion** warnings
- **Service downtime** immediate alerts

## Support

### Documentation
- **API Documentation**: Available at `/api/v1/docs`
- **Analytics Documentation**: Available at `/docs`
- **Grafana Dashboards**: Pre-configured monitoring
- **Runbooks**: Step-by-step operational procedures

### Getting Help
1. Check service health endpoints
2. Review application logs
3. Monitor resource usage
4. Verify configuration files
5. Test network connectivity between services

For additional support, refer to the main project documentation or contact the development team.
