#!/bin/bash

# First Res-Q Quick Setup Script
# This script automates the setup process for new users

echo "🚑 First Res-Q Setup Script 🚑"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not available. Please install Docker Desktop with Compose."
    exit 1
fi

# Test docker compose command
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Desktop with Compose."
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo "✅ Docker Compose found: $(docker compose version --short)"

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating environment file..."
    mkdir -p backend
    cat > backend/.env << EOF
ANYTHINGLLM_API_KEY=your_api_key_here
ANYTHINGLLM_WORKSPACE_ID=qhelper
EOF
    echo "✅ Created backend/.env file"
    echo "   You can edit this file to add your AnythingLLM API key if needed"
else
    echo "✅ Environment file already exists"
fi

# Build and start services
echo "🏗️  Building and starting services..."
echo "   This may take several minutes on first run..."

if docker compose up -d --build; then
    echo "✅ Services started successfully!"
else
    echo "❌ Failed to start services. Check the error messages above."
    exit 1
fi

# Check for port conflicts
echo "🔍 Checking for port conflicts..."
PORTS=(3000 8000 8080 6333 11434)
CONFLICTS=()

for port in "${PORTS[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        CONFLICTS+=($port)
    fi
done

if [ ${#CONFLICTS[@]} -gt 0 ]; then
    echo "⚠️  Warning: The following ports are already in use: ${CONFLICTS[*]}"
    echo "   You may need to stop other services or change port mappings in compose.yaml"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 20

# Check if services are responding
echo "🔍 Checking service health..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is ready"
else
    echo "⚠️  Backend not responding yet"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is ready"
else
    echo "⚠️  Frontend not responding yet"
fi

# Check if Ollama is responding (with retries)
OLLAMA_READY=false
for i in {1..6}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama is ready"
        OLLAMA_READY=true
        break
    else
        echo "⏳ Waiting for Ollama... (attempt $i/6)"
        sleep 10
    fi
done

if [ "$OLLAMA_READY" = true ]; then
    # Download a model
    echo "📦 Downloading AI model (phi3:mini)..."
    echo "   This may take a few minutes..."
    
    if docker exec ollama ollama pull phi3:mini; then
        echo "✅ Model downloaded successfully!"
    else
        echo "⚠️  Model download failed, but you can download it manually later"
        echo "   Run: docker exec ollama ollama pull phi3:mini"
    fi
else
    echo "⚠️  Ollama not responding after 60 seconds"
    echo "   Services are running, but you may need to download models manually"
    echo "   Try: docker exec ollama ollama pull phi3:mini"
fi

echo ""
echo "🎉 Setup Complete! 🎉"
echo "===================="
echo ""
echo "Your First Res-Q application is now running!"
echo ""
echo "📱 Access Points:"
echo "   Main App:        http://localhost:3000"
echo "   Backend API:     http://localhost:8000"
echo "   Ollama Web UI:   http://localhost:8080"
echo "   Qdrant Dashboard: http://localhost:6333/dashboard"
echo ""
echo "💡 Next Steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Try asking: 'How do I treat a burn?'"
echo "   3. Visit http://localhost:8080 to manage AI models"
echo ""
echo "🛠️  Useful Commands:"
echo "   View logs:       docker compose logs"
echo "   Stop services:   docker compose down"
echo "   Restart:         docker compose restart"
echo "   Download models: docker exec ollama ollama pull model_name"
echo "   Clean reset:     docker compose down -v && docker compose up -d --build"
echo ""
echo "🔧 Troubleshooting:"
echo "   If services fail to start:"
echo "   1. Check Docker Desktop is running"
echo "   2. Ensure ports aren't in use by other apps"
echo "   3. Try: docker compose down && docker compose up -d --build"
echo "   4. Check logs: docker compose logs [service_name]"
echo ""
echo "📚 For more information, see README.md"
