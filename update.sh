#!/bin/bash

echo "========================================"
echo "     QHelper-AI Update Script"
echo "========================================"
echo
echo "This script will update your existing QHelper-AI installation"
echo "with the latest code changes while preserving your downloaded models."
echo
echo "Prerequisites:"
echo "- Docker and Docker Compose are installed and running"
echo "- You have already run setup.sh before"
echo "- You have pulled the latest code with: git pull"
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo
echo "[1/4] Stopping existing containers..."
if ! docker compose down; then
    echo "ERROR: Failed to stop containers"
    echo "Make sure Docker is running and you're in the correct directory"
    exit 1
fi

echo
echo "[2/4] Rebuilding backend with new code..."
if ! docker compose build backend; then
    echo "ERROR: Failed to build backend"
    echo "Check the error messages above"
    exit 1
fi

echo
echo "[3/4] Rebuilding frontend with new code..."
if ! docker compose build frontend; then
    echo "ERROR: Failed to build frontend"
    echo "Check the error messages above"
    exit 1
fi

echo
echo "[4/5] Starting updated containers..."
if ! docker compose up -d; then
    echo "ERROR: Failed to start containers"
    echo "Check the error messages above"
    exit 1
fi

echo
echo "[5/5] Checking for missing AI model..."
echo "Waiting for Ollama to be ready..."
sleep 10

# Check if qwen2:1.5b is available
if ! docker exec ollama ollama list | grep -q "qwen2:1.5b"; then
    echo "Installing ultra-fast qwen2:1.5b model..."
    if docker exec ollama ollama pull qwen2:1.5b; then
        echo "✅ qwen2:1.5b downloaded successfully for maximum speed!"
    else
        echo "⚠️  qwen2:1.5b download failed. You can retry with:"
        echo "   docker exec ollama ollama pull qwen2:1.5b"
    fi
else
    echo "✅ qwen2:1.5b already available for ultra-fast responses"
fi

echo
echo "========================================"
echo "     Update Complete!"
echo "========================================"
echo
echo "Your QHelper-AI application has been updated with the latest changes."
echo
echo "✅ All downloaded models preserved (no re-download needed)"
echo "✅ Backend updated with latest code"
echo "✅ Frontend updated with latest code"
echo "✅ All containers running"
echo
echo "Access your application at:"
echo "🌐 Main App: http://localhost:3000"
echo "🔧 API Docs: http://localhost:8000/docs"
echo "❤️  Health:   http://localhost:8000/health"
echo
echo "Checking container status..."
docker compose ps
echo
echo "If you see any issues, check the logs with:"
echo "docker compose logs backend"
echo "docker compose logs frontend"
echo
