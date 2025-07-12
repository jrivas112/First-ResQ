from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://127.0.0.1:5500"] for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the enhanced RAG system with Ollama
print("Initializing Enhanced First Aid RAG system with Ollama...")
try:
    from enhanced_rag import EnhancedFirstAidRAG
    first_aid_rag = EnhancedFirstAidRAG(ollama_host=os.getenv("OLLAMA_HOST", "ollama:11434"))
    rag_initialized = first_aid_rag.initialize()
    if rag_initialized:
        print("✅ Enhanced RAG system initialized successfully!")
    else:
        print("❌ Enhanced RAG system failed to initialize, falling back to simple RAG")
        # Fallback to simple RAG
        from simple_rag import SimpleFirstAidRAG
        first_aid_rag = SimpleFirstAidRAG()
        rag_initialized = first_aid_rag.initialize()
except Exception as e:
    print(f"❌ Error loading enhanced RAG system: {e}")
    print("Falling back to simple RAG system...")
    try:
        from simple_rag import SimpleFirstAidRAG
        first_aid_rag = SimpleFirstAidRAG()
        rag_initialized = first_aid_rag.initialize()
    except Exception as e2:
        print(f"❌ Error loading simple RAG system: {e2}")
        first_aid_rag = None
        rag_initialized = False

# Request model for attachments
class Attachment(BaseModel):
    name: str
    mime: str
    contentString: str

# Request model for chat
class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "chat"
    sessionId: Optional[str] = None
    attachments: Optional[List[Attachment]] = []
    reset: Optional[bool] = False

@app.post("/ask")
async def ask_question(payload: ChatRequest):
    """Main endpoint - uses enhanced RAG system (RAG + Ollama)"""
    return await ask_local_rag(payload)

@app.post("/ask-rag-only")
async def ask_rag_only(payload: ChatRequest):
    """RAG-only endpoint - uses simple RAG system without LLM enhancement"""
    if not first_aid_rag or not rag_initialized:
        return {
            "error": "Local RAG system is not available",
            "textResponse": "The local AI system is currently unavailable. Please try again later."
        }
    
    try:
        # For RAG-only mode, we'll use the simple RAG system or force the enhanced one to skip Ollama
        if hasattr(first_aid_rag, 'search_similar_questions'):
            # Using enhanced RAG system but skipping Ollama
            similar_questions = first_aid_rag.search_similar_questions(payload.message, top_k=1)
            
            if similar_questions and similar_questions[0]['similarity'] > 0.1:
                best_match = similar_questions[0]
                return {
                    "textResponse": best_match['answer'],
                    "sources": [f"Question {best_match.get('index', 'N/A')}: {best_match['question'][:100]}..."],
                    "confidence": best_match['similarity'],
                    "type": "rag_only",
                    "method": "rag_only",
                    "similar_questions": [q['question'][:80] + "..." if len(q['question']) > 80 else q['question'] for q in similar_questions[:3]]
                }
            else:
                return {
                    "textResponse": "I don't have specific information about that in my knowledge base. For the best answer, try turning off 'RAG Only' mode to use AI enhancement.",
                    "confidence": 0.0,
                    "sources": [],
                    "type": "rag_only",
                    "method": "fallback",
                    "similar_questions": []
                }
        else:
            # Using simple RAG system
            result = first_aid_rag.get_answer(payload.message)
            result["method"] = "rag_only"
            return {
                "textResponse": result["answer"],
                "sources": [result["source"]] if result["source"] != "fallback" else [],
                "confidence": result["confidence"],
                "type": "rag_only",
                "method": result["method"],
                "similar_questions": result.get("similar_questions", [])
            }
            
    except Exception as e:
        return {
            "error": f"RAG-only system error: {str(e)}",
            "textResponse": "I'm sorry, there was an error processing your question. Please try again."
        }

@app.post("/ask-local")
async def ask_local_rag(payload: ChatRequest):
    """Ask question using enhanced RAG system with Ollama"""
    if not first_aid_rag or not rag_initialized:
        return {
            "error": "Local RAG system is not available",
            "textResponse": "The local AI system is currently unavailable. Please use the external AI option or try again later."
        }
    
    try:
        result = first_aid_rag.get_answer(payload.message)
        
        return {
            "textResponse": result["answer"],
            "sources": [result["source"]] if result["source"] != "fallback" else [],
            "confidence": result["confidence"],
            "type": "enhanced_local_rag",
            "method": result.get("method", "unknown"),
            "similar_questions": result.get("similar_questions", [])
        }
    except Exception as e:
        return {
            "error": f"Local RAG system error: {str(e)}",
            "textResponse": "I'm sorry, there was an error processing your question. Please try again."
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = "unknown"
    model_available = False
    
    # Check Ollama status
    try:
        import requests
        response = requests.get(f"http://{os.getenv('OLLAMA_HOST', 'ollama:11434')}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            ollama_status = "available"
            model_available = "phi3:mini" in model_names
        else:
            ollama_status = "unavailable"
    except Exception as e:
        ollama_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "rag_loaded": rag_initialized and first_aid_rag is not None,
        "total_qa_pairs": len(first_aid_rag.df) if first_aid_rag and first_aid_rag.df is not None else 0,
        "ollama_status": ollama_status,
        "phi3_mini_available": model_available,
        "enhanced_mode": rag_initialized and model_available
    }