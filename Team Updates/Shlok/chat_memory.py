import os
from supabase import create_client
from dotenv import load_dotenv

# ✅ Load env vars HERE
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY not set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_message(session_id: str, question: str, intent: dict):
    supabase.table("chat_history").insert({
        "session_id": session_id,
        "question": question,
        "intent": intent
    }).execute()

def get_last_messages(session_id: str, limit: int = 5):
    res = (
        supabase
        .table("chat_history")
        .select("question, intent")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(res.data)) if res.data else []
