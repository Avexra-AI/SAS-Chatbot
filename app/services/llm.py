from groq import Groq
import os
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_sql(user_query: str, semantic_layer: dict) -> str:
    """
    Generate SQL using LLM with semantic guardrails
    """

    semantic_text = json.dumps(semantic_layer, indent=2)

    prompt = f"""
You are a senior data analyst.

You MUST follow these rules:
- Use ONLY the tables, columns, and joins defined below
- DO NOT invent columns
- DO NOT calculate profit, tax, margin, GST
- If query is impossible, reply with: UNSUPPORTED

SEMANTIC LAYER:
{semantic_text}

USER QUESTION:
{user_query}

Return ONLY SQL. No explanation.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    if "UNSUPPORTED" in sql.upper():
        return ""

    return sql


def generate_nl_answer(user_query: str, sql: str, data: list) -> str:
    """
    Convert SQL result into natural language
    """

    prompt = f"""
User asked:
{user_query}

SQL executed:
{sql}

Result:
{json.dumps(data[:10], indent=2)}

You are a business analytics assistant.

Your job is to answer the user's question clearly and concisely 
using the provided data.

Rules:
- Do NOT explain SQL, joins, or tables
- Do NOT mention how the data was calculated
- Focus only on the business insight
- Keep the answer short and clear.
-Try to use minium tokens in answering the query and make the query as direct as you can.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
