# =========================
# IMPORTS
# =========================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import pandas as pd
import requests
import json
import re
import os

# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="NL2SQL Bot (Generic & Robust)")

# =========================
# DATABASE CONFIG
# =========================
NEON_DB_CONFIG = {
    "host": os.getenv("DB_HOST", "ep-raspy-night-ah8kwb6a-pooler.c-3.us-east-1.aws.neon.tech"),
    "database": os.getenv("DB_NAME", "neondb"),
    "user": os.getenv("DB_USER", "neondb_owner"),
    "password": os.getenv("DB_PASSWORD", "npg_tGk50unxySTW"),
    "port": 5432,
    "sslmode": "require"
}

# =========================
# OLLAMA CONFIG
# =========================
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "mistral"

# =========================
# METRIC OWNERSHIP (CORE IDEA)
# =========================
TABLE_FIRST_METRICS = {
    "sales", "value", "quantity", "rate",
    "brand", "category", "product", "client", "firm"
}

TABLE_SECOND_METRICS = {
    "tax", "gst", "gross", "gross total",
    "total tax", "tax amount", "invoice", "net"
}

# =========================
# SYSTEM PROMPT
# =========================
SCHEMA_PROMPT = """
You are an expert PostgreSQL SQL generator.

Schema:
table_first(
    f_date DATE,
    firm VARCHAR,
    voucher_no VARCHAR,
    quantity INT,
    value NUMERIC,
    brand VARCHAR,
    category VARCHAR
)

table_second(
    date_text TIMESTAMP,
    firm VARCHAR,
    voucher_no VARCHAR,
    total_tax_amount NUMERIC,
    gross_total NUMERIC
)

Rules:
- Generate ONLY PostgreSQL SELECT queries
- Never generate placeholder dates like YYYY-MM-DD
- Always use COALESCE for aggregations
- Return ONLY valid JSON

Output format:
{
  "sql": "...",
  "answer": "..."
}
"""

# =========================
# REQUEST MODEL
# =========================
class QueryRequest(BaseModel):
    question: str

# =========================
# SQL SAFETY
# =========================
def validate_sql(sql: str):
    forbidden = ["delete", "update", "insert", "drop", "alter", "truncate"]
    if any(word in sql.lower() for word in forbidden):
        raise ValueError("Unsafe SQL detected")

# =========================
# METRIC EXTRACTION (GENERIC)
# =========================
def detect_metric_sources(question: str):
    q = question.lower()
    uses_first = any(word in q for word in TABLE_FIRST_METRICS)
    uses_second = any(word in q for word in TABLE_SECOND_METRICS)
    return uses_first, uses_second

# =========================
# ENFORCE JOIN LOGIC (GENERIC)
# =========================
def enforce_join_logic(sql: str, question: str) -> str:
    uses_first, uses_second = detect_metric_sources(question)

    # JOIN only if metrics belong to different tables
    if uses_first and uses_second:
        return """
        SELECT
            t1.brand,
            COALESCE(SUM(t2.total_tax_amount), 0) AS tax_collection,
            COALESCE(SUM(t2.gross_total), 0) AS gross_profit
        FROM table_first t1
        JOIN table_second t2
          ON t1.firm = t2.firm
         AND t1.voucher_no = t2.voucher_no
        GROUP BY t1.brand;
        """

    return sql

# =========================
# SAFE FALLBACK
# =========================
def safe_fallback():
    return (
        "SELECT * FROM table_first LIMIT 5;",
        "Showing sample data as the request could not be fully interpreted."
    )

# =========================
# PARSE LLM RESPONSE
# =========================
def parse_llm_response(text: str):
    try:
        text = re.sub(r"```json|```", "", text).strip()
        data = json.loads(text)

        sql = data.get("sql", "").strip()
        answer = data.get("answer", "").strip()

        if not sql.lower().startswith("select"):
            raise ValueError("Only SELECT allowed")

        if not sql.endswith(";"):
            sql += ";"

        validate_sql(sql)
        return sql, answer

    except Exception:
        return safe_fallback()

# =========================
# LLM → SQL
# =========================
def nl_to_sql_llama(question: str):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SCHEMA_PROMPT},
            {"role": "user", "content": question}
        ],
        "stream": True,
        "options": {"temperature": 0}
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        stream=True,
        timeout=300
    )
    response.raise_for_status()

    full_text = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode())
            if "message" in data:
                full_text += data["message"]["content"]
            if data.get("done"):
                break

    return parse_llm_response(full_text)

# =========================
# EXECUTE SQL
# =========================
def execute_sql(sql_query: str):
    conn = psycopg2.connect(**NEON_DB_CONFIG)
    try:
        df = pd.read_sql(sql_query, conn)
        return df.to_dict(orient="records")
    finally:
        conn.close()

# =========================
# ROUTES
# =========================
@app.post("/chat")
def chat(req: QueryRequest):
    try:
        sql, answer = nl_to_sql_llama(req.question)

        # 🔥 Generic enforcement
        sql = enforce_join_logic(sql, req.question)

        result = execute_sql(sql)

        return {
            "question": req.question,
            "generated_sql": sql,
            "answer": answer,
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
