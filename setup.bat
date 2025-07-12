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
docker-compose --version >nul 2>&1
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

docker-compose up -d --build
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to start services. Check the error messages above.
    pause
    exit /b 1
)

echo ✅ Services started successfully!

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

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
echo    View logs:       docker-compose logs
echo    Stop services:   docker-compose down
echo    Restart:         docker-compose restart
echo    Download models: docker exec ollama ollama pull model_name
echo.
echo 📚 For more information, see README.md
echo.
pause
