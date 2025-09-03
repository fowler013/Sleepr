#!/bin/bash

# Sleepr Development Setup Script
# This script sets up the development environment for the Sleepr application

set -e

echo "🏈 Setting up Sleepr Fantasy Football App..."

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed. Please install Go 1.21+ and try again."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL 14+ and try again."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    
    # Generate a secure JWT secret
    JWT_SECRET=$(openssl rand -base64 32 2>/dev/null || echo "$(date +%s | sha256sum | base64 | head -c 32)")
    
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://localhost/sleepr?sslmode=disable

# Sleeper API
SLEEPER_API_BASE_URL=https://api.sleeper.app/v1

# Server Configuration
PORT=8080
ENVIRONMENT=development

# JWT Secret - Auto-generated secure key
JWT_SECRET=${JWT_SECRET}

# Analytics API
ANALYTICS_API_URL=http://localhost:8000
EOF
    echo "✅ Created .env file with secure JWT secret"
else
    echo "✅ .env file already exists"
fi

# Setup Go API
echo "🔧 Setting up Go API..."
cd api
go mod tidy
echo "✅ Go dependencies installed"
cd ..

# Setup Python Analytics
echo "🐍 Setting up Python Analytics..."
cd analytics

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created Python virtual environment"
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"
deactivate
cd ..

# Create database
echo "🗄️  Setting up database..."
createdb sleepr 2>/dev/null || echo "Database 'sleepr' may already exist"

# Run migrations
echo "📊 Running database migrations..."
cd api
go run cmd/server/main.go &
SERVER_PID=$!
sleep 2
kill $SERVER_PID 2>/dev/null || true
cd ..

echo "🎉 Sleepr setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with your database credentials"
echo "2. Start the API server: cd api && go run cmd/server/main.go"
echo "3. Start the analytics service: cd analytics && source venv/bin/activate && python src/api.py"
echo "4. Visit http://localhost:8080/health to verify the API is running"
echo "5. Visit http://localhost:8000/docs for analytics API documentation"
