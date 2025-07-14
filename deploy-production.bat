@echo off
REM Production deployment script for QHelper AI

echo 🚀 Deploying QHelper AI in Production Mode...

REM Stop any running development containers
echo 📦 Stopping existing containers...
docker compose down

REM Remove development volumes and build cache
echo 🧹 Cleaning up development artifacts...
docker system prune -f
docker volume prune -f

REM Build production images
echo 🏗️ Building production images...
docker compose build --no-cache

REM Start production services
echo 🌟 Starting production services...
docker compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to initialize...
timeout /t 30 /nobreak > nul

REM Download optimal model for production
echo 🤖 Setting up AI model...
docker exec ollama ollama pull qwen2:1.5b

REM Check service status
echo 🔍 Checking service status...
docker compose ps

echo.
echo ✅ Production deployment complete!
echo.
echo 🌐 Frontend (Nginx): http://localhost
echo 🔧 Ollama WebUI: http://localhost:8080
echo 📊 Backend API (internal): http://backend:8000
echo.
echo 📝 Note: Backend is now only accessible through Nginx proxy
echo 🔒 Production optimizations enabled: compression, caching, security headers

pause
