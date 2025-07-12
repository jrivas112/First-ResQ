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
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Desktop with Compose."
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo "✅ Docker Compose found: $(docker-compose --version)"

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

if docker-compose up -d --build; then
    echo "✅ Services started successfully!"
else
    echo "❌ Failed to start services. Check the error messages above."
    exit 1
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if Ollama is responding
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is ready"
    
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
    echo "⚠️  Ollama not responding yet, but services are starting"
    echo "   You can download models manually after startup completes"
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
echo "   View logs:       docker-compose logs"
echo "   Stop services:   docker-compose down"
echo "   Restart:         docker-compose restart"
echo "   Download models: docker exec ollama ollama pull model_name"
echo ""
echo "📚 For more information, see README.md"
