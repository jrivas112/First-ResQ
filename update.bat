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
echo [4/5] Starting updated containers...
docker compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start containers
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo [5/5] Checking for missing AI models...
echo Waiting for Ollama to be ready...
timeout /t 10 /nobreak >nul

REM Check if qwen2:1.5b is available
docker exec ollama ollama list | findstr "qwen2:1.5b" >nul
if errorlevel 1 (
    echo Installing ultra-fast qwen2:1.5b model...
    docker exec ollama ollama pull qwen2:1.5b
    if errorlevel 0 (
        echo ✅ qwen2:1.5b downloaded successfully
    ) else (
        echo ⚠️  qwen2:1.5b download failed
    )
) else (
    echo ✅ qwen2:1.5b already available
)

REM Check if phi3:mini is available
docker exec ollama ollama list | findstr "phi3:mini" >nul
if errorlevel 1 (
    echo Installing phi3:mini backup model...
    docker exec ollama ollama pull phi3:mini
    if errorlevel 0 (
        echo ✅ phi3:mini downloaded successfully
    ) else (
        echo ⚠️  phi3:mini download failed
    )
) else (
    echo ✅ phi3:mini already available
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
