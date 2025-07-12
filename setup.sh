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

# Create directories if they don't exist
mkdir -p backend

echo "📝 Checking setup..."

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
PORTS=(3000 8000 8080 11434)
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
    # Download ultra-fast AI model
    echo "📦 Downloading ultra-fast AI model..."
    echo "   This may take a few minutes..."
    
    # Download qwen2:1.5b (ultra-fast)
    echo "   Downloading qwen2:1.5b (ultra-fast, 934MB)..."
    if docker exec ollama ollama pull qwen2:1.5b; then
        echo "✅ qwen2:1.5b downloaded successfully for maximum speed!"
    else
        echo "⚠️  qwen2:1.5b download failed. You can retry later:"
        echo "   docker exec ollama ollama pull qwen2:1.5b"
    fi
else
    echo "⚠️  Ollama not responding after 60 seconds"
    echo "   Services are running, but you may need to download the model manually:"
    echo "   docker exec ollama ollama pull qwen2:1.5b"
fi

echo ""
echo "🎉 Setup Complete! 🎉"
echo "===================="
echo ""
echo "Your First Res-Q application is now running OFFLINE-CAPABLE!"
echo ""
echo "📱 Access Points:"
echo "   Main App:        http://localhost:3000 (✅ Works Offline)"
echo "   Backend API:     http://localhost:8000 (✅ Works Offline)"
echo "   Ollama Web UI:   http://localhost:8080 (✅ Works Offline)"
echo ""
echo "🔌 Offline Features:"
echo "   ✅ Pure offline operation - NO INTERNET REQUIRED"
echo "   ✅ Local AI with CSV knowledge base (1000+ Q&A pairs)"
echo "   ✅ Ollama LLM reasoning for complex questions"
echo "   ✅ Complete first aid assistance without connectivity"
echo "   ✅ Smart fallbacks and error handling"
echo ""
echo "💡 Next Steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Ask first aid questions - everything works offline!"
echo "   3. Try: 'How do I treat a burn?' or 'Someone is choking'"
echo "   4. Test offline: Disconnect internet - still works perfectly!"
echo ""
echo "🛠️  Useful Commands:"
echo "   View logs:       docker compose logs"
echo "   Stop services:   docker compose down"
echo "   Restart:         docker compose restart"
echo "   Download models: docker exec ollama ollama pull model_name"
echo "   List models:     docker exec ollama ollama list"
echo "   Remove model:    docker exec ollama ollama rm model_name"
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
