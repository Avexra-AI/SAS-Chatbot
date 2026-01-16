from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import json
import requests
import re
from dotenv import load_dotenv

from app.core.semantic import SemanticLayer
from app.core.chat_memory import save_message, get_last_messages

# ======================
# ENV
# ======================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not DATABASE_URL or not GROQ_API_KEY:
    raise RuntimeError("Missing environment variables")

# ======================
# PATH
# ======================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMANTIC_PATH = os.path.join(BASE_DIR, "semantic.json")

# ======================
# APP
# ======================
app = FastAPI(title="SAS Chatbot – NL2SQL")
semantic = SemanticLayer(SEMANTIC_PATH)

# ======================
# GROQ
# ======================
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

# ======================
# DB
# ======================
def run_sql(sql: str):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, r)) for r in rows]
    finally:
        conn.close()

# ======================
# REQUEST MODEL
# ======================
class Query(BaseModel):
    session_id: str
    question: str

# ======================
# INTENT EXTRACTION (WITH MEMORY)
# ======================
import re
import json

def extract_intent(question: str, history: list) -> dict:
    context = "\n".join(
        f"Q: {h['question']} | Intent: {h['intent']}"
        for h in history
    )

    prompt = f"""
You are an intent extraction engine.

Conversation history:
{context}

Return ONLY valid JSON in this EXACT format:

{{
  "metric": "",
  "dimensions": [],
  "filters": {{}}
}}

Allowed metrics:
- total_sales_amount
- units_sold
- item_revenue
- current_stock

Allowed dimensions:
- customer
- item
- voucher_date
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    res = requests.post(GROQ_URL, headers=headers, json=payload)
    if res.status_code != 200:
        raise RuntimeError(res.text)

    raw = res.json()["choices"][0]["message"]["content"].strip()

    # 1️⃣ Extract JSON block (non-greedy)
    match = re.search(r"\{[\s\S]*", raw)
    if not match:
        raise ValueError("LLM did not return JSON")

    json_text = match.group().strip()

    # 2️⃣ AUTO-REPAIR missing closing brace
    if json_text.count("{") > json_text.count("}"):
        json_text += "}"

    # 3️⃣ Parse JSON
    try:
        intent = json.loads(json_text)
    except json.JSONDecodeError:
        raise ValueError(f"Unrecoverable JSON from LLM:\n{json_text}")

    # 4️⃣ Structural validation
    if not all(k in intent for k in ("metric", "dimensions", "filters")):
        raise ValueError("Invalid intent structure")

    return intent

# ======================
# SQL BUILDER
# ======================
def build_sql(intent: dict) -> str:
    metric = semantic.get_metric(intent["metric"])
    base_model = semantic.get_model(metric["base_model"])

    if not intent["dimensions"]:
        return f"SELECT {metric['expression']} AS {intent['metric']} FROM {base_model['table']}"

    select = [f"{metric['expression']} AS {intent['metric']}"]
    group_by = []
    joins = []

    for d in intent["dimensions"]:
        dim = semantic.get_dimension(d)
        dim_model = semantic.get_model(dim["model"])

        select.append(f"{dim_model['table']}.{dim['column']} AS {d}")
        group_by.append(f"{dim_model['table']}.{dim['column']}")

        rel = semantic.get_relationship(dim["model"], metric["base_model"])
        parent = semantic.get_model(rel["from"])
        child = semantic.get_model(rel["to"])

        joins.append(
            f"JOIN {child['table']} ON {child['table']}.{rel['on']} = {parent['table']}.{parent['primary_key']}"
        )

    return (
        f"SELECT {', '.join(select)} "
        f"FROM {base_model['table']} "
        f"{' '.join(joins)} "
        f"GROUP BY {', '.join(group_by)}"
    )

# ======================
# API
# ======================
@app.post("/chat")
def chat(req: Query):
    try:
        history = get_last_messages(req.session_id)
        intent = extract_intent(req.question, history)
        semantic.validate(intent)

        sql = build_sql(intent)
        result = run_sql(sql)

        save_message(req.session_id, req.question, intent)

        return {
            "intent": intent,
            "sql": sql,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
