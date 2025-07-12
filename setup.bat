@echo off
echo ==============================================
echo First Res-Q Setup Script
echo ==============================================

REM ----------------------------------------------
REM 1️⃣ Prerequisites Check
REM ----------------------------------------------
echo.
echo Checking for Docker installation...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not installed. Please install Docker Desktop:
    echo     https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Checking for Docker Compose...
docker compose version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker Compose not found. Please ensure Docker Desktop includes Compose.
    pause
    exit /b 1
)

echo Docker and Docker Compose are installed.
echo.

REM ----------------------------------------------
REM 2️⃣ Ensure Required Directories Exist
REM ----------------------------------------------
if not exist "backend" mkdir backend

REM ----------------------------------------------
REM 3️⃣ Start Services with Docker Compose
REM ----------------------------------------------
echo Building and starting Docker services...
docker compose up -d --build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start services. Check error messages above.
    pause
    exit /b 1
)

echo Services started successfully.
echo.

REM ----------------------------------------------
REM 4️⃣ Port Conflict Check
REM ----------------------------------------------
echo Checking for port conflicts...
set "CONFLICT_FOUND="
for %%p in (3000 8000 8080 11434) do (
    netstat -an | findstr ":%%p " >nul 2>&1
    if not %ERRORLEVEL% EQU 1 (
        echo WARNING: Port %%p is already in use.
        set "CONFLICT_FOUND=1"
    )
)

if defined CONFLICT_FOUND (
    echo.
    echo WARNING: Some required ports are in use.
    echo    You may need to stop other applications or edit docker-compose.yml.
    set /p "CONTINUE=Continue anyway? (y/N): "
    if /i not "%CONTINUE%"=="y" (
        echo Setup cancelled.
        pause
        exit /b 1
    )
)
echo.

REM ----------------------------------------------
REM 5️⃣ Wait for Services to Initialize
REM ----------------------------------------------
echo Waiting for services to be ready...
timeout /t 20 /nobreak >nul

REM ----------------------------------------------
REM 6️⃣ Health Check - Backend
REM ----------------------------------------------
echo Checking backend health...
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Backend is responding.
) else (
    echo WARNING: Backend not responding yet.
)
echo.

REM ----------------------------------------------
REM 7️⃣ Health Check - Ollama
REM ----------------------------------------------
echo Checking Ollama readiness...
set "OLLAMA_READY="
for /l %%i in (1,1,6) do (
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Ollama is ready.
        set "OLLAMA_READY=1"
        goto :ollama_ready
    ) else (
        echo Waiting for Ollama... (attempt %%i/6)
        timeout /t 10 /nobreak >nul
    )
)

:ollama_ready
if defined OLLAMA_READY (
    echo Downloading ultra-fast AI model...
    echo    Downloading qwen2:1.5b (ultra-fast, 934MB)...
    docker exec ollama ollama pull qwen2:1.5b
    if %ERRORLEVEL% EQU 0 (
        echo ✅ qwen2:1.5b downloaded successfully for maximum speed!
    ) else (
        echo ⚠️  qwen2:1.5b download failed. You can retry later:
        echo     docker exec ollama ollama pull qwen2:1.5b
    )        ) else (
            echo ⚠️  qwen2:1.5b download failed. You can retry later:
            echo     docker exec ollama ollama pull qwen2:1.5b
        )
    ) else (
        echo ✅ qwen2:1.5b ready for ultra-fast responses!
    )
) else (
    echo WARNING: Ollama not responding after retries.
    echo    You can manually pull the model later:
    echo     docker exec ollama ollama pull qwen2:1.5b
    echo     docker exec ollama ollama pull mistral:latest
)
echo.

REM ----------------------------------------------
REM 8️⃣ Final Instructions
REM ----------------------------------------------
echo Setup Complete! Your First Res-Q app is now offline-capable.
echo ==============================================
echo.
echo Access Points:
echo    App:              http://localhost:3000
echo    Backend API:      http://localhost:8000
echo    Ollama UI:        http://localhost:8080
echo.
echo Offline Features:
echo    - Fully offline operation
echo    - Local AI with CSV knowledge base
echo    - Ollama LLM reasoning
echo    - Complete first aid help without internet
echo.
echo Next Steps:
echo    1. Open http://localhost:3000 in your browser
echo    2. Keep "Use Local AI" checked for offline mode
echo    3. Try questions like: "How do I treat a burn?"
echo    4. Disconnect internet to test offline support
echo.
echo Useful Commands:
echo    View logs:       docker compose logs
echo    Stop services:   docker compose down
echo    Restart:         docker compose restart
echo    Download model:  docker exec ollama ollama pull model_name
echo    Clean reset:     docker compose down -v && docker compose up -d --build
echo.
echo Troubleshooting:
echo    - Ensure Docker Desktop is running
echo    - Check for conflicting ports
echo    - Use: docker compose down && docker compose up -d --build
echo    - View logs for errors: docker compose logs [service]
echo.
echo See README.md for more details.
echo.
pause
