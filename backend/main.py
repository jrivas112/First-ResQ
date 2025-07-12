from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

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
API_URL = "http://localhost:3001/api/v1/workspace/qhelper/chat"

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