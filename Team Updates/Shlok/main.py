from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import json
import requests

from app.core.cache import get_from_cache, store_in_cache
from dotenv import load_dotenv
import os

load_dotenv()

# ======================
# APP
# ======================
app = FastAPI(title="SAS Chatbot – NL2SQL")

# ======================
# LOAD SEMANTIC LAYER
# ======================
with open("semantic.js") as f:
    SEMANTIC = json.load(f)

# ======================
# ENV
# ======================
DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"

# ======================
# DB
# ======================
def run_sql(sql):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

# ======================
# REQUEST MODEL
# ======================
class Query(BaseModel):
    question: str

# ======================
# GROQ → INTENT
# ======================
def extract_intent(question: str) -> dict:
    prompt = """
Return ONLY JSON:
{
  "metric": "",
  "dimensions": [],
  "filters": {}
}

Allowed metrics: total_sales_amount, item_revenue, current_stock
Allowed dimensions: customer, item
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
    res.raise_for_status()

    return json.loads(res.json()["choices"][0]["message"]["content"])

# ======================
# SEMANTIC VALIDATION
# ======================
def validate_semantic(intent):
    if intent["metric"] not in SEMANTIC["metrics"]:
        raise ValueError("Metric not allowed")

    for d in intent["dimensions"]:
        if d not in SEMANTIC["dimensions"]:
            raise ValueError(f"Dimension '{d}' not allowed")

# ======================
# SQL BUILDER
# ======================
def build_sql(intent):
    metric = intent["metric"]
    dims = intent["dimensions"]
    expr = SEMANTIC["metrics"][metric]["expression"]

    if metric == "total_sales_amount" and "customer" in dims:
        return f"""
        SELECT c.name AS customer, {expr} AS total_sales
        FROM customers c
        JOIN sales s ON c.id = s.customer_id
        GROUP BY c.name
        """

    if metric == "item_revenue":
        return f"""
        SELECT item_name, {expr} AS revenue
        FROM sales_items
        GROUP BY item_name
        """

    if metric == "current_stock":
        return f"""
        SELECT item_name, {expr} AS current_stock
        FROM stock_movements
        GROUP BY item_name
        """

    raise ValueError("Unsupported query")

# ======================
# API
# ======================
@app.post("/chat")
def chat(req: Query):
    try:
        # 1. Groq
        intent = extract_intent(req.question)

        # 2. Semantic governance
        validate_semantic(intent)

        # 3. Semantic cache
        cached = get_from_cache(intent)
        if cached:
            return cached

        # 4. SQL
        sql = build_sql(intent)

        # 5. DB
        result = run_sql(sql)

        # 6. Cache store
        store_in_cache(intent, sql.strip(), result)

        return {
            "source": "database",
            "intent": intent,
            "sql": sql.strip(),
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
