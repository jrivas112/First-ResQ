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

# Configs
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "YOUR_API_KEY")
ANYTHINGLLM_HOST = os.getenv("ANYTHINGLLM_HOST", "host.docker.internal")
API_URL = f"http://{ANYTHINGLLM_HOST}:3001/api/v1/workspace/qhelper/chat"

@app.post("/ask")
async def ask_question(payload: ChatRequest):
    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, json=payload.dict(), headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": "Failed to get response from AnythingLLM",
            "status_code": response.status_code,
            "details": response.text
        }