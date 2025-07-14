### 🚑 First Res-Q – Offline-First AI Emergency Assistant (Scroll down for setup instructions)

**First Res-Q** is a fully offline-capable **first aid chatbot** designed to assist in emergency situations without requiring an internet connection after initial setup. Built with a **FastAPI backend**, a responsive **HTML/CSS/JavaScript frontend**, and **containerized AI services**, it ensures reliable performance in any environment.

The system uses a **Retrieval-Augmented Generation (RAG)** pipeline grounded in a curated database of frequently asked first aid questions. When a user submits a query, the system searches for the most relevant entry in the database and passes it to **Ollama**, which uses the retrieved context to generate accurate, grounded responses.

## ✅ Key Features

- **100% offline** functionality after initial setup  
- AI-powered, context-aware responses using RAG + Ollama  
- Grounded in real first aid data for higher accuracy  
- Lightweight and containerized for portability  
- **Privacy-first design**: all data stays local, no cloud or third-party services  
- **Encrypted user profiles**: AES-256 encryption with a shared passphrase  
- **Guest Mode**: use the app without storing any personal data  

**No internet required after initial setup!**

## 💻 Development Note
This application was developed and optimized on **Snapdragon X-Elite** hardware. The fast CPU and generous memory of the X-Elite platform made development incredibly smooth, allowing for rapid iteration and testing of AI models. The efficient architecture makes it perfect for deployment on modern ARM-based systems while maintaining full compatibility with traditional x86 platforms.

## 🚀 Features

- **🔌 Pure Offline Operation** - Works completely without internet after setup
- **Interactive Chat Interface** - Ask first aid questions and get immediate responses
- **Enhanced Local AI** - Combines CSV knowledge base with Ollama LLM for intelligent responses
- **Smart Response Methods**:
  - 🤖 **AI + Knowledge Base** - Best responses using both RAG and LLM reasoning
  - 🤖 **AI Reasoning** - Ollama-powered responses for general questions
  - 📚 **Knowledge Base Only** - Fast CSV lookup when LLM unavailable
  - 🆘 **General Advice** - Safety fallback for unmatched queries
- **600+ First Aid Q&A Pairs** - Comprehensive emergency knowledge base
- **Web UI for AI Models** - Manage local models via Ollama Web UI
- **Containerized Architecture** - Complete Docker setup for easy deployment
- **Cross-Platform** - Runs on Windows, macOS, and Linux
- **Health Monitoring** - Built-in health checks and system status

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
**Docker Must Be installed**
- **Docker Desktop** (latest version) https://www.docker.com/
- **Docker Compose** (usually included with Docker Desktop)
- **Git** (for cloning the repository)

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Storage**: At least 10GB free space for models and containers
- **CPU**: Multi-core processor (GPU optional but not required)

## 🛠️ Installation & Setup
**Make sure you download and install docker**
1) **!!Open docker desktop application before doing the following commands!!**
### 1. Clone the Repository

```bash
git clone https://github.com/jrivas112/QHelper-AI.git
cd QHelper-AI
```

### 2. Quick Start

**Option A: Use Setup Scripts (Recommended) in root project directory**

**Windows:**
```batch
./setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Option B: Manual Setup**

```bash
# Build and start all services
docker compose up -d --build

# Wait for services to start
sleep 20

# Download AI model (optional but recommended)
docker exec ollama ollama pull qwen2:1.5b
```

### 3. Build and Start Services

From the root directory:

```bash
# Build and start all services
docker compose up --build

# Or run in background (detached mode)
docker compose up -d --build
```

**First startup will take several minutes** as Docker downloads all the necessary images.

### 4. Download AI Model

Once the containers are running, download the ultra-fast AI model:

```bash
# Download ultra-fast model (automatically used by setup scripts)
docker exec ollama ollama pull qwen2:1.5b

# Verify the model was downloaded
docker exec ollama ollama list
```
## IF IT DOESNT WORK AFTER INSTALLING THE MODEL
run the following commands:
```bash
docker compose down

docker compose build

docker compose up -d

```
**Wait 10-20 seconds for all the services to start**

**Model Performance:**
- `qwen2:1.5b` (934MB) - Ultra-fast responses, minimal memory usage, perfect for emergency first aid

**Note:** Setup scripts automatically download this model for maximum speed. Additional models can be added manually if needed.

### 5. Verify Installation

Check that all services are running:

```bash
# Check container status
docker compose ps

# You should see all containers as "Up"
```

## 🌐 Access Points

Once everything is running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **First Res-Q App** | http://localhost:3000 | Main chat application |
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Health Check** | http://localhost:8000/health | System status |
| **Ollama Web UI** | http://localhost:8080 | Model management interface |

## 💬 Using the Application

1. **Open the main app** at http://localhost:3000
2. **Ask first aid questions** - The system automatically uses the best available method
3. **Get intelligent responses** with method indicators:
   - 🤖 **AI + Knowledge Base** - Enhanced responses using both CSV data and LLM reasoning
   - 🤖 **AI Reasoning** - Pure LLM responses when no specific knowledge found
   - 📚 **Knowledge Base Only** - Direct CSV matches when Ollama unavailable
   - 🆘 **General Advice** - Safe fallback responses

### Example Questions to Try:
- "What should I do for a minor cut?"
- "How do I help someone who is choking?"
- "What are the signs of a heart attack?"
- "How do I treat a sprain?"
- "My child is bleeding"
- "Someone is unconscious"

**Note**: The system works completely offline after the initial setup and model download.

## 🔧 Configuration Options

### Using Different AI Models

```bash
# List available models
docker exec ollama ollama list

# Pull ultra-fast models (recommended)
docker exec ollama ollama pull qwen2:1.5b     # 934MB - Ultra-fast
docker exec ollama ollama pull gemma:2b       # 1.4GB - Very fast

# Pull balanced models
docker exec ollama ollama pull phi3:mini      # 2.2GB - Fast & quality
docker exec ollama ollama pull mistral:latest # 4.1GB - Best quality

# Pull larger models (if you have sufficient RAM)
docker exec ollama ollama pull llama2:7b      # 3.8GB - Good quality
docker exec ollama ollama pull llama2:13b     # 7GB - Excellent quality

# Remove models to save space
docker exec ollama ollama rm model_name
```

**Current Model Priority:**
1. `qwen2:1.5b` - Ultra-fast (934MB)
2. `phi3:mini` - Fast backup (2.2GB) 
3. `mistral:latest` - Quality backup (4.1GB)

The system automatically uses the fastest available model.

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

## � Updating the Application

When new code updates are available, you can update your installation while preserving your downloaded models:

### Quick Update (Recommended)

**Windows:**
```batch
# Pull latest changes
git pull

# Run update script
update.bat
```

**Linux/macOS:**
```bash
# Pull latest changes
git pull

# Run update script
./update.sh
```

### Manual Update

If you prefer to update manually:

```bash
# 1. Pull latest code
git pull

# 2. Stop containers
docker compose down

# 3. Rebuild with new code
docker compose build

# 4. Start updated containers
docker compose up -d
```

**Important Notes:**
- ✅ **Models preserved**: Downloaded Ollama models are kept (no re-download needed)
- ✅ **Data preserved**: All configuration and cache files maintained
- ✅ **Quick process**: Only rebuilds application code, not base images

## �🛑 Stopping the Application

```bash
# Stop all services
docker compose down

# Stop and remove all data (WARNING: This deletes downloaded models)
docker compose down --volumes
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
docker compose restart ollama

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

### ⚡ Speed Optimization Options

Your system is already optimized for maximum speed with qwen2:1.5b!

#### **1. Current Ultra-Fast Configuration**
```bash
# Your setup automatically uses the fastest model available
docker exec ollama ollama list  # Should show qwen2:1.5b (934MB)

# Test the ultra-fast response
docker exec ollama ollama run qwen2:1.5b "How do I treat a cut?"
```

#### **2. Model Performance (Current Setup)**
| Model | Size | Speed | Quality | Status |
|-------|------|-------|---------|--------|
| `qwen2:1.5b` | 934MB | ⚡⚡⚡ | Good | **✅ Primary (Auto-installed)** |
| `phi3:mini` | 2.2GB | ⚡⚡ | Excellent | Fallback option |
| `mistral:latest` | 4.1GB | ⚡ | Excellent | Manual install only |

#### **3. Why qwen2:1.5b is Perfect for First Aid**
- **🚀 Ultra-fast**: ~1-2 second response times
- **💾 Minimal RAM**: Uses <1GB memory
- **⚡ Instant startup**: Model loads quickly
- **🎯 Emergency-focused**: Optimized for quick, clear responses

#### **4. Hardware Optimizations**
- **RAM**: Allocate more memory to Docker (8GB+ recommended)
- **Storage**: Use SSD for Docker volumes if available
- **CPU**: Close other applications to free up processing power

#### **5. Quick Model Switching**
To prioritize a different model, edit `backend/enhanced_rag.py` line 26:
```python
# For maximum speed:
self.preferred_models = ["qwen2:1.5b", "gemma:2b", "phi3:mini", ...]

# For balanced performance (current):
self.preferred_models = ["phi3:mini", "gemma:2b", "mistral:latest", ...]

# For maximum quality:
self.preferred_models = ["mistral:latest", "phi3:mini", "gemma:2b", ...]
```

Then rebuild: `docker compose build backend && docker compose up backend -d`

#### **6. Response Length Control**
The system now uses optimized parameters:
- **Shorter responses**: Faster generation (current: ~250 tokens max)
- **Focused answers**: Reduced token sampling for quicker decisions
- **Smart timeouts**: 30-second limit prevents hanging

## 📁 Project Structure

```
QHelper-AI/
├── compose.yaml              # Docker services configuration
├── README.md                 # This documentation
├── backend/                  # FastAPI backend
│   ├── dockerfile           # Backend container config
│   ├── requirements.txt     # Python dependencies
│   ├── main.py             # FastAPI application
│   ├── enhanced_rag.py     # Enhanced RAG + Ollama system
│   ├── firstaidqa-*.csv    # First aid Q&A dataset
│   ├── main.py             # FastAPI backend application
│   ├── requirements.txt    # Python dependencies
│   └── dockerfile          # Backend container configuration
├── frontend/               # Static web frontend
│   ├── dockerfile         # Frontend container config
│   ├── index.html         # Main HTML page
│   ├── chatbot.js         # Chat functionality
│   └── nginx.conf         # Web server config
└── style.css              # Application styling
```

## 🧠 RAG Systems Overview

This project includes multiple Retrieval-Augmented Generation (RAG) implementations, each designed for different scenarios and capabilities:

### 📊 `enhanced_rag.py` - **Primary System** (Hybrid AI + Knowledge Base)
**Purpose**: Main production RAG system combining CSV knowledge with Ollama LLM reasoning
- **Technology**: TF-IDF vectorization + Ollama AI integration
- **Capabilities**: 
  - Searches CSV knowledge base for relevant first aid information
  - Enhances answers using Ollama LLM for better context and reasoning
  - Provides intelligent fallback responses when no exact matches found
  - Offers three response modes: RAG+Ollama, Ollama-only, or RAG-only
- **Use Case**: Primary system used by the main application
- **Advantages**: Best balance of accuracy, intelligence, and offline capability

### 🔄 Enhanced RAG Workflow

The Enhanced RAG system follows this detailed workflow when processing user questions:

#### 1. **Initialization Phase**
```
🚀 System Startup
├── Load CSV dataset (641 first aid Q&A pairs)
├── Generate/load TF-IDF vectors for questions
├── Test Ollama connection and discover available models
├── Select best model (mistral:latest → phi3:mini → fallback)
└── Initialize complete ✅
```

#### 2. **Query Processing Phase**
```
📝 User asks: "How do I treat a burn?"
├── Preprocess text (lowercase, clean, normalize)
├── Convert to TF-IDF vector
├── Calculate cosine similarity with all knowledge base questions
└── Return top 3 most similar questions with similarity scores
```

#### 3. **Response Generation Phase**
The system uses a **decision tree** to determine the best response method:

**🎯 Decision Logic:**
```
High similarity match found (>0.05)?
├── YES: Use RAG + Ollama Enhancement
│   ├── Extract best matching answer from knowledge base
│   ├── Create enhanced prompt with context
│   ├── Send to Ollama via /api/chat endpoint
│   └── Return: AI-enhanced response with knowledge base context
│
└── NO: Use Ollama-Only Mode
    ├── Create general first aid prompt
    ├── Send to Ollama for reasoning
    └── Return: AI-generated response without specific knowledge base match
```

#### 4. **Ollama Integration Details**
```
🤖 Ollama API Call Process:
├── Endpoint: /api/chat (instead of /api/generate for better completion)
├── Format: Message-based conversation structure
├── Parameters:
│   ├── Model: mistral:latest (preferred) or best available
│   ├── Temperature: 0.7 (balanced creativity/consistency)
│   ├── num_predict: 500 (reasonable response length)
│   ├── top_k: 40, top_p: 0.9 (quality controls)
│   └── No stop sequences (allow natural completion)
├── Timeout: 60 seconds (accommodate model thinking time)
└── Response: Extract content from message.content field
```

#### 5. **Fallback Mechanisms**
```
🛡️ Multi-Level Fallback System:
├── Level 1: Ollama unavailable → Use pure RAG (knowledge base only)
├── Level 2: No knowledge base match → General safety advice
├── Level 3: Complete system failure → Error message with safety guidance
└── Always available: RAG-only mode toggle for fastest responses
```

#### 6. **Response Assembly**
```
📤 Final Response Structure:
├── answer: "Detailed first aid instructions..."
├── confidence: 0.85 (similarity score + AI enhancement boost)
├── source: "AI enhanced with knowledge from similar case"
├── method: "rag_plus_ollama" | "ollama_only" | "rag_only" | "fallback"
├── similar_questions: ["Related question 1", "Related question 2", ...]
└── Additional metadata for debugging and transparency
```

## 📊 Confidence Level Calculation

The system calculates confidence scores to indicate how reliable each response is. Understanding these scores helps users assess the trustworthiness of the provided first aid advice.

### **Confidence Score Ranges**

| Score Range | Meaning | Response Quality |
|-------------|---------|------------------|
| **0.8 - 1.0** | 🟢 **High Confidence** | Excellent match with knowledge base + AI enhancement |
| **0.5 - 0.79** | 🟡 **Medium Confidence** | Good AI reasoning or strong knowledge base match |
| **0.1 - 0.49** | 🟠 **Low Confidence** | Weak knowledge base match, limited context |
| **0.0** | 🔴 **No Confidence** | Fallback response, seek professional help |

### **How Confidence is Calculated**

#### **Method 1: RAG + Ollama (rag_plus_ollama)**
```
Base Confidence = TF-IDF Similarity Score (0.0 - 1.0)
Enhancement Boost = +0.3 (for AI reasoning improvement)
Final Confidence = min(0.9, Base + Enhancement)

Example:
├── TF-IDF similarity: 0.65 (good match for "bleeding treatment")
├── AI enhancement: +0.30 (Ollama expands and improves response)
└── Final confidence: min(0.9, 0.65 + 0.30) = 0.9 🟢
```

#### **Method 2: Ollama Only (ollama_only)**
```
Fixed Confidence = 0.5 (medium confidence)
Reason: Pure AI reasoning without specific knowledge base context

Example:
├── No strong knowledge base match found (similarity < 0.05)
├── Ollama generates response from general training
└── Confidence: 0.5 🟡 (reliable AI but no specific first aid data)
```

#### **Method 3: RAG Only (rag_only)**
```
Confidence = TF-IDF Similarity Score (direct match)

Example:
├── TF-IDF similarity: 0.72 (good match in knowledge base)
├── Ollama unavailable, using direct CSV answer
└── Confidence: 0.72 🟡 (good knowledge match but no AI enhancement)
```

#### **Method 4: Fallback (fallback)**
```
Confidence = 0.0 (no confidence)
Reason: No knowledge base match + no AI available

Example:
├── Question: "How to fix my car engine?"
├── No relevant first aid knowledge found
└── Confidence: 0.0 🔴 (recommends consulting professionals)
```

### **Confidence Factors**

#### **TF-IDF Similarity Thresholds**
- **≥ 0.1**: Minimum threshold for knowledge base usage
- **≥ 0.05**: Minimum threshold for Ollama enhancement
- **< 0.05**: Triggers Ollama-only or fallback mode

#### **Response Quality Indicators**
- **High confidence (0.8+)**: Use advice with confidence, but still verify for serious emergencies
- **Medium confidence (0.5-0.79)**: Good guidance, consider additional verification
- **Low confidence (0.1-0.49)**: Basic guidance only, seek professional help
- **No confidence (0.0)**: Do not rely on advice, consult medical professionals immediately

### **Practical Usage Examples**

```json
{
  "question": "How do I stop severe bleeding?",
  "confidence": 0.87,
  "method": "rag_plus_ollama",
  "interpretation": "🟢 High confidence - Strong knowledge base match + AI enhancement"
}

{
  "question": "What should I do if someone faints?",
  "confidence": 0.52,
  "method": "ollama_only", 
  "interpretation": "🟡 Medium confidence - AI reasoning without specific match"
}

{
  "question": "How to treat a broken bone?",
  "confidence": 0.23,
  "method": "rag_only",
  "interpretation": "🟠 Low confidence - Weak knowledge match, no AI available"
}

{
  "question": "How to repair a car?", 
  "confidence": 0.0,
  "method": "fallback",
  "interpretation": "🔴 No confidence - Not a first aid question, seek appropriate help"
}
```

#### 7. **Performance Optimizations**
- **Vector Caching**: TF-IDF vectors cached to disk for instant startup
- **Model Selection**: Automatic best-model detection with fallback hierarchy
- **Connection Pooling**: Persistent connections to Ollama service
- **Smart Prompting**: Context-aware prompts that guide AI responses
- **Response Streaming**: Uses chat endpoint for more complete responses

#### 8. **Quality Assurance**
- **Debug Logging**: Comprehensive request/response logging for troubleshooting
- **Health Checks**: Continuous monitoring of Ollama model availability
- **Response Validation**: Ensures non-empty, meaningful responses before returning

### 🎯 Enhanced RAG System

**Primary System**: `enhanced_rag.py` - Production-ready RAG with AI enhancement
- **Technology**: TF-IDF vectorization + Ollama LLM integration
- **Capabilities**:
  - Smart conversation context management
  - Multi-modal response generation (RAG + AI)
  - Cached TF-IDF vectors for fast similarity search
  - Model-specific optimizations for speed and quality
  - Graceful degradation when AI services are unavailable
- **Use Case**: Primary system for all medical assistance queries
- **Advantages**: High-quality responses, context awareness, reliable fallback mechanisms

## 🔄 Development Workflow

### Making Changes

1. **Backend changes**: Edit files in `backend/`, then restart:
   ```bash
   docker compose restart backend
   ```

2. **Frontend changes**: Edit files in `frontend/`, then rebuild:
   ```bash
   docker compose up --build frontend
   ```

3. **Configuration changes**: Edit `compose.yaml`, then:
   ```bash
   docker compose down
   docker compose up --build
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


## 🆘 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker compose logs service_name`
3. Create an issue with detailed error information
4. Include your system specifications and Docker version

## 🔗 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---
## 🔐 Security

**First Res-Q** is designed with privacy and security at its core. Here’s how it protects user data:

### 1. Fully Local Operation
All components of the application — including the chatbot, AI processing, and data storage — run entirely on the user's device.

- No data is sent to the cloud  
- No external APIs are called  
- No third-party analytics are used  

This ensures **maximum privacy** and complete control over your data.

### 2. Client-Side Encryption
User profiles are encrypted directly in the browser using:

- **AES-GCM** with a 256-bit key  
- Key derived via **PBKDF2** with 200,000 iterations  

Even if someone gains access to your browser’s local storage, the encrypted data is **unreadable without the correct passphrase**.

### 3. Single Passphrase Model
The app uses a **shared passphrase** to encrypt and unlock all user profiles. This is not per-user authentication, but a simplified encryption model designed for:

- Trusted, offline environments  
- Single-user or family use cases  

On first load, users are prompted to create a passphrase. On subsequent visits, they can:

- Enter the passphrase to unlock profiles  
- Or proceed in **Guest Mode**, where no personal data is stored or accessed

### 4. No Server-Side Authentication
There’s no need for:

- Server-side login systems  
- Multi-user password storage  
- External identity providers  

This keeps the system **lightweight, secure, and easy to use**, while maintaining strong data protection standards.

## Contast Us
- https://www.linkedin.com/in/juliomidence/
- https://www.linkedin.com/in/krutadnyata-khandu-naik-745484129/
- https://www.linkedin.com/in/amrutha-challa-b6a208223/
- https://www.linkedin.com/in/saya-deshpande/
**Happy First Aid Learning! 🚑💡**
