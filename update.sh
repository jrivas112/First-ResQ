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
echo "[4/4] Starting updated containers..."
if ! docker compose up -d; then
    echo "ERROR: Failed to start containers"
    echo "Check the error messages above"
    exit 1
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
