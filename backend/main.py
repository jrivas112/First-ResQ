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
        print("❌ Enhanced RAG system failed to initialize")
        first_aid_rag = None
        rag_initialized = False
except Exception as e:
    print(f"❌ Error loading enhanced RAG system: {e}")
    first_aid_rag = None
    rag_initialized = False

# Request model for attachments
class Attachment(BaseModel):
    name: str
    mime: str
    contentString: str

# Request model for profile information
class ProfileInfo(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    pre_existing_conditions: Optional[str] = None

# Request model for chat
class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "chat"
    sessionId: Optional[str] = None
    attachments: Optional[List[Attachment]] = []
    reset: Optional[bool] = False
    profile: Optional[ProfileInfo] = None

@app.post("/ask")
async def ask_question(payload: ChatRequest):
    """Main endpoint - uses enhanced RAG system (RAG + Ollama)"""
    if not first_aid_rag or not rag_initialized:
        return {
            "error": "Local RAG system is not available",
            "textResponse": "The local AI system is currently unavailable. Please use the external AI option or try again later."
        }
    
    try:
        # Convert profile to dict if provided
        profile_dict = None
        profile_id = "guest"  # Default profile ID
        
        # Debug: Show what we received in the request
        print(f"=== API REQUEST DEBUG ===")
        print(f"Message: {payload.message}")
        print(f"SessionId: {payload.sessionId}")
        print(f"Profile: {payload.profile}")
        
        if payload.profile:
            profile_dict = {
                'age': payload.profile.age,
                'gender': payload.profile.gender,
                'blood_group': payload.profile.blood_group,
                'pre_existing_conditions': payload.profile.pre_existing_conditions
            }
            print(f"Profile dict created: {profile_dict}")
        
        # Extract profile ID from session or payload
        if hasattr(payload, 'sessionId') and payload.sessionId:
            profile_id = payload.sessionId
            print(f"Using profile ID from sessionId: {profile_id}")
        
        print(f"Calling get_answer with profile_id: {profile_id}, profile_dict: {profile_dict}")
        
        result = first_aid_rag.get_answer(payload.message, profile_dict, profile_id)
        
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

@app.post("/ask-rag-only")
async def ask_rag_only(payload: ChatRequest):
    """RAG-only endpoint - uses simple RAG system without LLM enhancement"""
    if not first_aid_rag or not rag_initialized:
        return {
            "error": "Local RAG system is not available",
            "textResponse": "The local AI system is currently unavailable. Please try again later."
        }
    
    try:
        # For RAG-only mode, use the enhanced RAG system but skip Ollama
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
            
    except Exception as e:
        return {
            "error": f"RAG-only system error: {str(e)}",
            "textResponse": "I'm sorry, there was an error processing your question. Please try again."
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = "unknown"
    available_models = []
    selected_model = None
    
    # Check Ollama status
    try:
        import requests
        response = requests.get(f"http://{os.getenv('OLLAMA_HOST', 'ollama:11434')}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            available_models = [model.get("name", "") for model in models]
            ollama_status = "available"
            
            # Get the selected model from the RAG system if available
            if first_aid_rag and hasattr(first_aid_rag, 'get_best_model'):
                try:
                    selected_model = first_aid_rag.get_best_model()
                except:
                    selected_model = available_models[0] if available_models else None
        else:
            ollama_status = "unavailable"
    except Exception as e:
        ollama_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "rag_loaded": rag_initialized and first_aid_rag is not None,
        "total_qa_pairs": len(first_aid_rag.df) if first_aid_rag and first_aid_rag.df is not None else 0,
        "ollama_status": ollama_status,
        "available_models": available_models,
        "selected_model": selected_model,
        "enhanced_mode": rag_initialized and len(available_models) > 0
    }

class ClearConversationRequest(BaseModel):
    sessionId: str = "guest"

@app.post("/clear-conversation")
async def clear_conversation(request: ClearConversationRequest):
    """Clear conversation history for a specific profile"""
    try:
        if first_aid_rag and hasattr(first_aid_rag, 'clear_profile_history'):
            first_aid_rag.clear_profile_history(request.sessionId)
            return {
                "status": "success",
                "message": f"Conversation history cleared for profile: {request.sessionId}"
            }
        else:
            return {
                "status": "info", 
                "message": "No conversation history to clear"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error clearing conversation: {str(e)}"
        }

@app.get("/conversation-summary")
async def get_conversation_summary(sessionId: str = "guest"):
    """Get current conversation summary"""
    try:
        if first_aid_rag and hasattr(first_aid_rag, 'get_conversation_summary'):
            summary = first_aid_rag.get_conversation_summary(sessionId)
            return {
                "status": "success",
                **summary
            }
        else:
            return {
                "status": "info",
                "total_exchanges": 0,
                "recent_topics": [],
                "context_enabled": False,
                "profile_id": sessionId
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting conversation summary: {str(e)}"
        }