# app/api/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.orchestrator import handle_query

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest):
    answer = handle_query(req.message)
    return {"answer": answer}
