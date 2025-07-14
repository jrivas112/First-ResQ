#!/bin/bash
# Production deployment script for QHelper AI

echo "🚀 Deploying QHelper AI in Production Mode..."

# Stop any running development containers
echo "📦 Stopping existing containers..."
docker compose down

# Remove development volumes and build cache
echo "🧹 Cleaning up development artifacts..."
docker system prune -f
docker volume prune -f

# Build production images
echo "🏗️ Building production images..."
docker compose build --no-cache

# Start production services
echo "🌟 Starting production services..."
docker compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Download optimal model for production
echo "🤖 Setting up AI model..."
docker exec ollama ollama pull qwen2:1.5b

# Check service status
echo "🔍 Checking service status..."
docker compose ps

echo ""
echo "✅ Production deployment complete!"
echo ""
echo "🌐 Frontend (Nginx): http://localhost"
echo "🔧 Ollama WebUI: http://localhost:8080"
echo "📊 Backend API (internal): http://backend:8000"
echo ""
echo "📝 Note: Backend is now only accessible through Nginx proxy"
echo "🔒 Production optimizations enabled: compression, caching, security headers"
