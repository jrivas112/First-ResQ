@echo off
echo 🚑 First Res-Q Setup Script 🚑
echo ==================================

REM Check if Docker is installedecho 🔌 Offline Features:
echo    ✅ Pure offline operation - NO INTERNET REQUIRED
echo    ✅ Local AI with CSV knowledge base (1000+ Q&A pairs)
echo    ✅ Ollama LLM reasoning for complex questions
echo    ✅ Complete first aid assistance without connectivity
echo    ✅ Smart fallbacks and error handling
echo.
echo 💡 Next Steps:
echo    1. Open http://localhost:3000 in your browser
echo    2. Ask first aid questions - everything works offline!
echo    3. Try: 'How do I treat a burn?' or 'Someone is choking'
echo    4. Test offline: Disconnect internet - still works perfectly!
echo.ersion >nul 2>&1
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

REM Create directories if they don't exist
if not exist "backend" mkdir backend

echo 📝 Checking setup...

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
echo Your First Res-Q application is now running OFFLINE-CAPABLE!
echo.
echo 📱 Access Points:
echo    Main App:         http://localhost:3000 (✅ Works Offline)
echo    Backend API:      http://localhost:8000 (✅ Works Offline)
echo    Ollama Web UI:    http://localhost:8080 (✅ Works Offline)
echo    Qdrant Dashboard: http://localhost:6333/dashboard (✅ Works Offline)
echo.
echo � Offline Features:
echo    ✅ Local AI with CSV knowledge base (always available)
echo    ✅ Ollama LLM reasoning (available after model download)
echo    ✅ Complete first aid assistance without internet
echo    ✅ Smart fallbacks for any connectivity issues
echo.
echo �💡 Next Steps:
echo    1. Open http://localhost:3000 in your browser
echo    2. Keep "Use Local AI" checked for offline operation
echo    3. Try asking: 'How do I treat a burn?'
echo    4. Test offline: Disconnect internet and still get help!
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
