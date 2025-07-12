@echo off
echo ========================================
echo     QHelper-AI Update Script
echo ========================================
echo.
echo This script will update your existing QHelper-AI installation
echo with the latest code changes while preserving your downloaded models.
echo.
echo Prerequisites:
echo - Docker Desktop is running
echo - You have already run setup.bat before
echo - You have pulled the latest code with: git pull
echo.
pause

echo.
echo [1/4] Stopping existing containers...
docker compose down
if errorlevel 1 (
    echo ERROR: Failed to stop containers
    echo Make sure Docker Desktop is running
    pause
    exit /b 1
)

echo.
echo [2/4] Rebuilding backend with new code...
docker compose build backend
if errorlevel 1 (
    echo ERROR: Failed to build backend
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo [3/4] Rebuilding frontend with new code...
docker compose build frontend
if errorlevel 1 (
    echo ERROR: Failed to build frontend
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo [4/4] Starting updated containers...
docker compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start containers
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo     Update Complete!
echo ========================================
echo.
echo Your QHelper-AI application has been updated with the latest changes.
echo.
echo ✅ All downloaded models preserved (no re-download needed)
echo ✅ Backend updated with latest code
echo ✅ Frontend updated with latest code
echo ✅ All containers running
echo.
echo Access your application at:
echo 🌐 Main App: http://localhost:3000
echo 🔧 API Docs: http://localhost:8000/docs
echo ❤️  Health:   http://localhost:8000/health
echo.
echo Checking container status...
docker compose ps
echo.
echo If you see any issues, check the logs with:
echo docker compose logs backend
echo docker compose logs frontend
echo.
pause
