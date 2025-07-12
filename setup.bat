@echo off
echo 🚑 First Res-Q Setup Script 🚑
echo ==================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker compose version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not available. Please install Docker Desktop with Compose.
    pause
    exit /b 1
)

echo ✅ Docker found
echo ✅ Docker Compose found

REM Create .env file if it doesn't exist
if not exist "backend\.env" (
    echo 📝 Creating environment file...
    if not exist "backend" mkdir backend
    (
        echo ANYTHINGLLM_API_KEY=your_api_key_here
        echo ANYTHINGLLM_WORKSPACE_ID=qhelper
    ) > backend\.env
    echo ✅ Created backend\.env file
    echo    You can edit this file to add your AnythingLLM API key if needed
) else (
    echo ✅ Environment file already exists
)

REM Build and start services
echo 🏗️  Building and starting services...
echo    This may take several minutes on first run...

docker compose up -d --build
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to start services. Check the error messages above.
    pause
    exit /b 1
)

echo ✅ Services started successfully!

REM Check for port conflicts
echo 🔍 Checking for port conflicts...
set "CONFLICT_FOUND="
for %%p in (3000 8000 8080 6333 11434) do (
    netstat -an | findstr ":%%p " >nul 2>&1
    if not %ERRORLEVEL% EQU 1 (
        echo ⚠️  Warning: Port %%p is already in use
        set "CONFLICT_FOUND=1"
    )
)

if defined CONFLICT_FOUND (
    echo    You may need to stop other services or change port mappings in compose.yaml
    set /p "CONTINUE=Continue anyway? (y/N): "
    if /i not "%CONTINUE%"=="y" (
        echo ❌ Setup cancelled
        pause
        exit /b 1
    )
)

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 20 /nobreak >nul

REM Check if services are responding
echo 🔍 Checking service health...

REM Check backend (using curl if available, or ping as fallback)
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend is ready
) else (
    echo ⚠️  Backend not responding yet
)

REM Check if Ollama is responding (with retries)
set "OLLAMA_READY="
for /l %%i in (1,1,6) do (
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Ollama is ready
        set "OLLAMA_READY=1"
        goto :ollama_ready
    ) else (
        echo ⏳ Waiting for Ollama... (attempt %%i/6)
        timeout /t 10 /nobreak >nul
    )
)

:ollama_ready
if defined OLLAMA_READY (
    REM Download a model
    echo 📦 Downloading AI model (phi3:mini)...
    echo    This may take a few minutes...

    docker exec ollama ollama pull phi3:mini
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Model downloaded successfully!
    ) else (
        echo ⚠️  Model download failed, but you can download it manually later
        echo    Run: docker exec ollama ollama pull phi3:mini
    )
) else (
    echo ⚠️  Ollama not responding after 60 seconds
    echo    Services are running, but you may need to download models manually
    echo    Try: docker exec ollama ollama pull phi3:mini
)

echo.
echo 🎉 Setup Complete! 🎉
echo ====================
echo.
echo Your First Res-Q application is now running!
echo.
echo 📱 Access Points:
echo    Main App:         http://localhost:3000
echo    Backend API:      http://localhost:8000
echo    Ollama Web UI:    http://localhost:8080
echo    Qdrant Dashboard: http://localhost:6333/dashboard
echo.
echo 💡 Next Steps:
echo    1. Open http://localhost:3000 in your browser
echo    2. Try asking: 'How do I treat a burn?'
echo    3. Visit http://localhost:8080 to manage AI models
echo.
echo 🛠️  Useful Commands:
echo    View logs:       docker compose logs
echo    Stop services:   docker compose down
echo    Restart:         docker compose restart
echo    Download models: docker exec ollama ollama pull model_name
echo    Clean reset:     docker compose down -v ^&^& docker compose up -d --build
echo.
echo 🔧 Troubleshooting:
echo    If services fail to start:
echo    1. Check Docker Desktop is running
echo    2. Ensure ports aren't in use by other apps
echo    3. Try: docker compose down ^&^& docker compose up -d --build
echo    4. Check logs: docker compose logs [service_name]
echo.
echo 📚 For more information, see README.md
echo.
pause
