.PHONY: help setup build run test clean docker

# Default target
help:
	@echo "Sleepr Fantasy Football App - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  setup     - Initial project setup"
	@echo "  run-api   - Run the Go API server"
	@echo "  run-analytics - Run the Python analytics service"
	@echo "  run-all   - Run both API and analytics services"
	@echo ""
	@echo "Database:"
	@echo "  db-create - Create the database"
	@echo "  db-migrate - Run database migrations"
	@echo "  db-seed   - Seed database with sample data"
	@echo "  db-reset  - Reset database (drop and recreate)"
	@echo ""
	@echo "Testing:"
	@echo "  test      - Run all tests"
	@echo "  test-api  - Run Go API tests"
	@echo "  test-analytics - Run Python analytics tests"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build     - Build the application"
	@echo "  clean     - Clean build artifacts"
	@echo "  docker    - Build Docker containers"

# Setup
setup:
	@echo "🚀 Setting up Sleepr..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

# Run services
run-api:
	@echo "🏈 Starting API server..."
	@cd api && go run cmd/server/main.go

run-analytics:
	@echo "🧠 Starting analytics service..."
	@cd analytics && source venv/bin/activate && python src/api.py

run-all:
	@echo "🚀 Starting all services..."
	@make run-api &
	@make run-analytics &
	@wait

# Database operations
db-create:
	@echo "📊 Creating database..."
	@createdb sleepr || echo "Database may already exist"

db-migrate:
	@echo "📈 Running database migrations..."
	@cd api && go run cmd/migrate/main.go

db-seed:
	@echo "🌱 Seeding database..."
	@psql -d sleepr -f database/seeds/sample_data.sql

db-reset:
	@echo "🔄 Resetting database..."
	@dropdb sleepr || true
	@make db-create
	@make db-migrate
	@make db-seed

# Testing
test:
	@make test-api
	@make test-analytics

test-api:
	@echo "🧪 Running Go tests..."
	@cd api && go test ./...

test-analytics:
	@echo "🔬 Running Python tests..."
	@cd analytics && source venv/bin/activate && python -m pytest

# Build
build:
	@echo "🔨 Building application..."
	@cd api && go build -o ../bin/sleepr-api cmd/server/main.go
	@echo "✅ Build complete"

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf bin/
	@cd api && go clean
	@echo "✅ Clean complete"

# Docker
docker:
	@echo "🐳 Building Docker containers..."
	@docker-compose build
	@echo "✅ Docker build complete"

# Install dependencies
deps:
	@echo "📦 Installing dependencies..."
	@cd api && go mod tidy
	@cd analytics && source venv/bin/activate && pip install -r requirements.txt

# Development utilities
dev-deps:
	@echo "🛠 Installing development dependencies..."
	@go install github.com/air-verse/air@latest
	@cd analytics && source venv/bin/activate && pip install jupyter black flake8 pytest

watch-api:
	@echo "👀 Starting API with hot reload..."
	@cd api && air

format:
	@echo "💅 Formatting code..."
	@cd api && go fmt ./...
	@cd analytics && source venv/bin/activate && black src/

lint:
	@echo "🔍 Linting code..."
	@cd api && go vet ./...
	@cd analytics && source venv/bin/activate && flake8 src/
