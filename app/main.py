from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from backend/
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

from fastapi import FastAPI
from app.api.chat import router as chat_router

app = FastAPI(title="SAS Chatbot")

app.include_router(chat_router, prefix="/api")
