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
    """Main endpoint - uses local RAG system"""
    return await ask_local_rag(payload)

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
    return {
        "status": "healthy",
        "rag_loaded": rag_initialized and first_aid_rag is not None,
        "total_qa_pairs": len(first_aid_rag.df) if first_aid_rag and first_aid_rag.df is not None else 0
    }