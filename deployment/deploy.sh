#!/bin/bash
set -e

# Sleepr Deployment Script
# Automates the deployment of Sleepr fantasy football application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE=${1:-docker}  # docker, kubernetes, local
ENVIRONMENT=${2:-development}  # development, staging, production
PROJECT_NAME="sleepr"
DOCKER_REGISTRY="ghcr.io/fowler013"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    case $DEPLOYMENT_TYPE in
        "docker")
            command -v docker >/dev/null 2>&1 || error "Docker is required but not installed."
            command -v docker-compose >/dev/null 2>&1 || error "Docker Compose is required but not installed."
            ;;
        "kubernetes")
            command -v kubectl >/dev/null 2>&1 || error "kubectl is required but not installed."
            command -v helm >/dev/null 2>&1 || warning "Helm is recommended for Kubernetes deployments."
            ;;
        "local")
            command -v go >/dev/null 2>&1 || error "Go is required but not installed."
            command -v node >/dev/null 2>&1 || error "Node.js is required but not installed."
            command -v python3 >/dev/null 2>&1 || error "Python3 is required but not installed."
            ;;
    esac
    
    success "Prerequisites check completed"
}

# Environment setup
setup_environment() {
    log "Setting up environment for $ENVIRONMENT..."
    
    # Create environment file if it doesn't exist
    ENV_FILE=".env.${ENVIRONMENT}"
    if [[ ! -f $ENV_FILE ]]; then
        log "Creating $ENV_FILE..."
        cat > $ENV_FILE << EOF
# Sleepr Environment Configuration - $ENVIRONMENT
NODE_ENV=$ENVIRONMENT
GO_ENV=$ENVIRONMENT
PYTHON_ENV=$ENVIRONMENT

# Database
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_USER=sleepr_user
POSTGRES_DB=sleepr

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)

# JWT
JWT_SECRET=$(openssl rand -base64 64)

# Monitoring
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# API URLs
API_URL=http://localhost:8080
ANALYTICS_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
EOF
    fi
    
    success "Environment setup completed"
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    # Build API image
    log "Building API image..."
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}-api:latest ./api/
    
    # Build Analytics image
    log "Building Analytics image..."
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}-analytics:latest ./analytics/
    
    # Build Frontend image
    log "Building Frontend image..."
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:latest ./web/frontend/
    
    success "Docker images built successfully"
}

# Deploy with Docker Compose
deploy_docker() {
    log "Deploying with Docker Compose..."
    
    # Copy environment file
    cp .env.${ENVIRONMENT} .env
    
    # Start services
    docker-compose -f deployment/docker-compose.yml down --remove-orphans
    docker-compose -f deployment/docker-compose.yml up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    timeout 300 bash -c 'until docker-compose -f deployment/docker-compose.yml ps | grep -q "healthy"; do sleep 5; done'
    
    success "Docker deployment completed"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl create namespace $PROJECT_NAME --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply secrets
    kubectl create secret generic sleepr-secrets \
        --from-env-file=.env.${ENVIRONMENT} \
        --namespace=$PROJECT_NAME \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy application
    kubectl apply -f deployment/kubernetes/sleepr-deployment.yaml
    
    # Wait for rollout
    kubectl rollout status deployment/sleepr-api -n $PROJECT_NAME
    kubectl rollout status deployment/sleepr-analytics -n $PROJECT_NAME
    kubectl rollout status deployment/sleepr-frontend -n $PROJECT_NAME
    
    success "Kubernetes deployment completed"
}

# Local development deployment
deploy_local() {
    log "Setting up local development environment..."
    
    # Start database services
    docker-compose -f deployment/docker-compose.yml up -d postgres redis
    
    # Wait for databases
    sleep 10
    
    # Run database migrations
    cd api && go run cmd/migrate/main.go up && cd ..
    
    # Start API server
    log "Starting API server..."
    cd api && go run cmd/server/main.go &
    API_PID=$!
    cd ..
    
    # Start Analytics server
    log "Starting Analytics server..."
    cd analytics && python -m uvicorn api.main:app --reload --port 8001 &
    ANALYTICS_PID=$!
    cd ..
    
    # Start Frontend
    log "Starting Frontend..."
    cd web/frontend && npm start &
    FRONTEND_PID=$!
    cd ../..
    
    # Save PIDs for cleanup
    echo $API_PID > .api.pid
    echo $ANALYTICS_PID > .analytics.pid
    echo $FRONTEND_PID > .frontend.pid
    
    success "Local development environment started"
    log "API: http://localhost:8080"
    log "Analytics: http://localhost:8001"
    log "Frontend: http://localhost:3000"
    log "Use './deploy.sh stop local' to stop services"
}

# Stop local services
stop_local() {
    log "Stopping local services..."
    
    if [[ -f .api.pid ]]; then
        kill $(cat .api.pid) 2>/dev/null || true
        rm .api.pid
    fi
    
    if [[ -f .analytics.pid ]]; then
        kill $(cat .analytics.pid) 2>/dev/null || true
        rm .analytics.pid
    fi
    
    if [[ -f .frontend.pid ]]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
    fi
    
    # Stop database services
    docker-compose -f deployment/docker-compose.yml down postgres redis
    
    success "Local services stopped"
}

# Health check
health_check() {
    log "Performing health check..."
    
    case $DEPLOYMENT_TYPE in
        "docker")
            docker-compose -f deployment/docker-compose.yml ps
            ;;
        "kubernetes")
            kubectl get pods -n $PROJECT_NAME
            kubectl get services -n $PROJECT_NAME
            ;;
        "local")
            curl -f http://localhost:8080/api/v1/health || warning "API health check failed"
            curl -f http://localhost:8001/health || warning "Analytics health check failed"
            curl -f http://localhost:3000 || warning "Frontend health check failed"
            ;;
    esac
    
    success "Health check completed"
}

# Cleanup function
cleanup() {
    log "Performing cleanup..."
    
    case $DEPLOYMENT_TYPE in
        "docker")
            docker-compose -f deployment/docker-compose.yml down --remove-orphans
            docker system prune -f
            ;;
        "kubernetes")
            kubectl delete namespace $PROJECT_NAME --ignore-not-found=true
            ;;
        "local")
            stop_local
            ;;
    esac
    
    success "Cleanup completed"
}

# Main deployment logic
main() {
    log "Starting Sleepr deployment..."
    log "Deployment type: $DEPLOYMENT_TYPE"
    log "Environment: $ENVIRONMENT"
    
    case $1 in
        "stop")
            if [[ $DEPLOYMENT_TYPE == "local" ]]; then
                stop_local
            else
                cleanup
            fi
            ;;
        "health")
            health_check
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            check_prerequisites
            setup_environment
            
            case $DEPLOYMENT_TYPE in
                "docker")
                    build_images
                    deploy_docker
                    ;;
                "kubernetes")
                    build_images
                    deploy_kubernetes
                    ;;
                "local")
                    deploy_local
                    ;;
                *)
                    error "Unknown deployment type: $DEPLOYMENT_TYPE"
                    ;;
            esac
            
            health_check
            ;;
    esac
    
    success "Deployment completed successfully!"
}

# Script usage
usage() {
    echo "Usage: $0 [DEPLOYMENT_TYPE] [ENVIRONMENT] [ACTION]"
    echo ""
    echo "DEPLOYMENT_TYPE:"
    echo "  docker      - Deploy using Docker Compose (default)"
    echo "  kubernetes  - Deploy to Kubernetes cluster"
    echo "  local       - Local development setup"
    echo ""
    echo "ENVIRONMENT:"
    echo "  development - Development environment (default)"
    echo "  staging     - Staging environment"
    echo "  production  - Production environment"
    echo ""
    echo "ACTION:"
    echo "  (default)   - Deploy the application"
    echo "  stop        - Stop the application"
    echo "  health      - Check application health"
    echo "  cleanup     - Clean up deployment"
    echo ""
    echo "Examples:"
    echo "  $0                              # Deploy with Docker in development"
    echo "  $0 kubernetes production        # Deploy to Kubernetes in production"
    echo "  $0 local development           # Start local development environment"
    echo "  $0 docker development stop     # Stop Docker deployment"
}

# Handle help flag
if [[ $1 == "-h" || $1 == "--help" ]]; then
    usage
    exit 0
fi

# Run main function
main $3
