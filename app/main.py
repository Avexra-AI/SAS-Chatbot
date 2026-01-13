# from dotenv import load_dotenv
# from pathlib import Path

# # Explicitly load .env from backend/
# ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
# load_dotenv(dotenv_path=ENV_PATH)

# from fastapi import FastAPI
# from app.api.chat import router as chat_router

# app = FastAPI(title="SAS Chatbot")

# app.include_router(chat_router, prefix="/api")
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load .env from backend/
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router

app = FastAPI(title="SAS Chatbot")

# 🔥 CORS CONFIGURATION (REQUIRED FOR FRONTEND)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],             # Allows OPTIONS, POST, GET
    allow_headers=["*"],             # Allows Content-Type, Authorization
)

# API routes
app.include_router(chat_router, prefix="/api")


# uvicorn app.main:app --reload