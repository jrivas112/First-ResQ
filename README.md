# First Res-Q - AI-Powered First Aid Assistant

A comprehensive first aid chatbot application with local AI capabilities, built with FastAPI backend, HTML/CSS/JS frontend, and containerized AI services.

## 🚀 Features

- **Interactive Chat Interface** - Ask first aid questions and get immediate responses
- **Local AI Models** - Run LLM models locally using Ollama (no external API dependencies)
- **Vector Database** - RAG (Retrieval-Augmented Generation) capabilities with Qdrant
- **Web UI** - User-friendly interface for model management
- **Containerized** - Complete Docker setup for easy deployment
- **Cross-Platform** - Runs on Windows, macOS, and Linux

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (latest version)
- **Docker Compose** (usually included with Docker Desktop)
- **Git** (for cloning the repository)

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Storage**: At least 10GB free space for models and containers
- **CPU**: Multi-core processor (GPU optional but not required)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd QHelper-AI
```

### 2. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
# Navigate to backend directory
cd backend

# Create .env file (Windows)
echo ANYTHINGLLM_API_KEY=your_api_key_here > .env
echo ANYTHINGLLM_WORKSPACE_ID=qhelper >> .env

# Create .env file (macOS/Linux)
cat > .env << EOF
ANYTHINGLLM_API_KEY=your_api_key_here
ANYTHINGLLM_WORKSPACE_ID=qhelper
EOF
```

**Note**: Replace `your_api_key_here` with your actual AnythingLLM API key, or leave it as is if you plan to use only local AI models.

### 3. Build and Start Services

From the root directory:

```bash
# Build and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

**First startup will take several minutes** as Docker downloads all the necessary images.

### 4. Download AI Models

Once the containers are running, download an AI model:

```bash
# Download a small, fast model (recommended for testing)
docker exec ollama ollama pull phi3:mini

# Or download a larger, more capable model
docker exec ollama ollama pull llama2:7b

# Verify the model was downloaded
docker exec ollama ollama list
```

### 5. Verify Installation

Check that all services are running:

```bash
# Check container status
docker-compose ps

# You should see all containers as "Up"
```

## 🌐 Access Points

Once everything is running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **First Res-Q App** | http://localhost:3000 | Main chat application |
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Ollama Web UI** | http://localhost:8080 | Model management interface |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector database admin |

## 💬 Using the Application

1. **Open the main app** at http://localhost:3000
2. **Type a first aid question** like "How do I treat a burn?"
3. **Get AI-powered responses** based on medical knowledge

### Example Questions to Try:
- "What should I do for a minor cut?"
- "How do I help someone who is choking?"
- "What are the signs of a heart attack?"
- "How do I treat a sprain?"

## 🔧 Configuration Options

### Using Different AI Models

```bash
# List available models online
docker exec ollama ollama list

# Pull different models
docker exec ollama ollama pull codellama:7b
docker exec ollama ollama pull mistral:7b
docker exec ollama ollama pull llama2:13b

# Remove models to save space
docker exec ollama ollama rm model_name
```

### Backend Configuration

Edit `backend/main.py` to:
- Change API endpoints
- Modify CORS settings
- Add new routes
- Integrate additional services

### Frontend Customization

Edit files in `frontend/` to:
- Modify the UI (`index.html`, `style.css`)
- Change chat behavior (`chatbot.js`)
- Add new features

## 🛑 Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (WARNING: This deletes downloaded models)
docker-compose down --volumes
```

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Check what's using the port
netstat -ano | findstr :3000

# Kill the process or change ports in compose.yaml
```

**2. Out of memory/disk space**
```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune
```

**3. Models not appearing in Web UI**
```bash
# Restart ollama container
docker-compose restart ollama

# Re-download model
docker exec ollama ollama pull phi3:mini
```

**4. Backend can't connect to services**
```bash
# Check if all containers are in the same network
docker network ls
docker network inspect qhelper-ai_appnet
```

### Windows WSL Issues

If you encounter GPU-related errors on Windows:
1. The application will automatically fall back to CPU mode
2. Models will run slower but still function
3. Consider using smaller models like `phi3:mini`

### Performance Optimization

**For faster responses:**
- Use smaller models (`phi3:mini`, `llama2:7b`)
- Allocate more RAM to Docker Desktop
- Use SSD storage for Docker volumes

**For better quality:**
- Use larger models (`llama2:13b`, `llama2:70b`)
- Ensure adequate RAM (16GB+ recommended)

## 📁 Project Structure

```
QHelper-AI/
├── compose.yaml              # Docker services configuration
├── README.md                 # This documentation
├── backend/                  # FastAPI backend
│   ├── dockerfile           # Backend container config
│   ├── requirements.txt     # Python dependencies
│   ├── main.py             # FastAPI application
│   ├── local_rag.py        # RAG implementation
│   ├── getdatabase.py      # Database utilities
│   └── .env                # Environment variables
├── frontend/               # Static web frontend
│   ├── dockerfile         # Frontend container config
│   ├── index.html         # Main HTML page
│   ├── chatbot.js         # Chat functionality
│   └── nginx.conf         # Web server config
└── style.css              # Application styling
```

## 🔄 Development Workflow

### Making Changes

1. **Backend changes**: Edit files in `backend/`, then restart:
   ```bash
   docker-compose restart backend
   ```

2. **Frontend changes**: Edit files in `frontend/`, then rebuild:
   ```bash
   docker-compose up --build frontend
   ```

3. **Configuration changes**: Edit `compose.yaml`, then:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Adding New Models

```bash
# Research available models
docker exec ollama ollama list --help

# Pull specific model
docker exec ollama ollama pull model_name:tag

# Test model
curl http://localhost:11434/api/generate -d '{
  "model": "model_name",
  "prompt": "Test prompt",
  "stream": false
}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker-compose logs service_name`
3. Create an issue with detailed error information
4. Include your system specifications and Docker version

## 🔗 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**Happy First Aid Learning! 🚑💡**
