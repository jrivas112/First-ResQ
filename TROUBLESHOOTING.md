# 🛠️ Troubleshooting Guide

## Quick Diagnostics

### Check Service Status
```bash
# See all running containers
docker-compose ps

# Check logs for specific service
docker-compose logs backend
docker-compose logs ollama
docker-compose logs frontend
```

### Test Connectivity
```bash
# Test Ollama API
curl http://localhost:11434/api/tags

# Test Backend API
curl http://localhost:8000/docs

# Test Qdrant
curl http://localhost:6333/collections
```

## Common Issues & Solutions

### 🚫 "Port already in use" Error

**Problem**: Another service is using the required ports.

**Solution**:
```bash
# Find what's using the port (Windows)
netstat -ano | findstr :3000

# Find what's using the port (macOS/Linux)
lsof -i :3000

# Kill the process or change ports in compose.yaml
```

### 🐳 Docker Issues

**Problem**: Docker containers won't start.

**Solutions**:
```bash
# Clean up Docker system
docker system prune -a

# Remove unused volumes
docker volume prune

# Restart Docker Desktop
# (Use Docker Desktop interface)

# Check Docker daemon is running
docker info
```

### 🧠 Models Not Loading/Working

**Problem**: AI models not responding or missing.

**Solutions**:
```bash
# Check if models are downloaded
docker exec ollama ollama list

# Re-download model
docker exec ollama ollama pull phi3:mini

# Restart Ollama service
docker-compose restart ollama

# Check Ollama logs
docker-compose logs ollama
```

### 🌐 Web UI Not Accessible

**Problem**: Can't access web interfaces.

**Solutions**:
```bash
# Check if services are running
docker-compose ps

# Verify network connectivity
docker network ls
docker network inspect qhelper-ai_appnet

# Restart all services
docker-compose restart

# Access using container IP directly
docker inspect frontend | grep IPAddress
```

### 💾 Out of Memory/Disk Space

**Problem**: System running out of resources.

**Solutions**:
```bash
# Check disk usage
docker system df

# Clean up unused images
docker image prune -a

# Remove stopped containers
docker container prune

# Remove unused volumes (WARNING: Deletes data)
docker volume prune
```

### ⚡ Slow Performance

**Problem**: Application runs slowly.

**Solutions**:
- Use smaller AI models (`phi3:mini` instead of `llama2:70b`)
- Allocate more RAM to Docker Desktop (Settings → Resources)
- Use SSD storage for Docker volumes
- Close other resource-heavy applications

### 🔗 Backend API Errors

**Problem**: Backend can't connect to other services.

**Solutions**:
```bash
# Check environment variables
docker exec backend env | grep -E "(OLLAMA|QDRANT|ANYTHINGLLM)"

# Test internal connectivity
docker exec backend curl http://ollama:11434/api/tags
docker exec backend curl http://qdrant:6333/collections

# Restart backend with fresh build
docker-compose up --build backend
```

### 🖥️ Windows WSL Issues

**Problem**: GPU-related errors on Windows.

**Solutions**:
- Remove GPU configuration (already done in current setup)
- Use CPU-only mode (default in current setup)
- Ensure WSL 2 is being used
- Update Docker Desktop to latest version

### 🔑 Environment Variables Not Loading

**Problem**: API keys or configuration not working.

**Solutions**:
```bash
# Check .env file format (no spaces around =)
cat backend/.env

# Recreate .env file
echo "ANYTHINGLLM_API_KEY=your_key" > backend/.env
echo "ANYTHINGLLM_WORKSPACE_ID=qhelper" >> backend/.env

# Restart services after .env changes
docker-compose down
docker-compose up -d
```

## Performance Optimization

### Model Selection Guide

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `phi3:mini` | ~2GB | Fast | Good | Testing, development |
| `llama2:7b` | ~4GB | Medium | Better | General use |
| `llama2:13b` | ~7GB | Slow | Best | High quality responses |
| `codellama:7b` | ~4GB | Medium | Good | Code-related queries |

### Resource Allocation

**Minimum Requirements**:
- RAM: 8GB (4GB for system + 4GB for models)
- Storage: 10GB free space
- CPU: 2+ cores

**Recommended Setup**:
- RAM: 16GB (8GB for system + 8GB for models)
- Storage: 50GB free space (SSD preferred)
- CPU: 4+ cores

## Emergency Reset

If everything breaks and you need to start fresh:

```bash
# Nuclear option - removes everything
docker-compose down --volumes --remove-orphans
docker system prune -a --volumes
docker volume prune

# Then restart setup
./setup.sh   # Linux/macOS
setup.bat    # Windows
```

## Getting Help

### Log Collection for Support

```bash
# Collect all logs
docker-compose logs > debug_logs.txt

# Get system info
docker info > docker_info.txt
docker-compose ps > container_status.txt

# Check resource usage
docker stats --no-stream > resource_usage.txt
```

### Useful Commands Reference

```bash
# Service management
docker-compose up -d          # Start in background
docker-compose down           # Stop services
docker-compose restart        # Restart all services
docker-compose logs -f        # Follow logs in real-time

# Container management
docker exec -it ollama bash   # Access container shell
docker exec ollama ollama list # Run commands in container

# Cleanup
docker system df              # Check disk usage
docker system prune           # Clean unused resources
docker-compose pull           # Update images
```

### Still Need Help?

1. Check this troubleshooting guide first
2. Search existing issues in the repository
3. Create a new issue with:
   - Error messages (full text)
   - System information (OS, Docker version)
   - Steps to reproduce
   - Logs from failing services
