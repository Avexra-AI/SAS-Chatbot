# app/core/orchestrator.py

from app.core.semantic import SemanticLayer
from app.services.llm import generate_sql, generate_nl_answer
from app.db.session import run_query
from app.utils.serialization import normalize_data

semantic = SemanticLayer()


def handle_query(user_query: str):
    """
    End-to-end flow:
    User → LLM SQL → DB → LLM NL answer
    """

    # 1️⃣ Generate SQL using LLM + semantic guardrails
    sql = generate_sql(
        user_query=user_query,
        semantic_layer=semantic.layer
    )

    if not sql:
        return {
            "answer": "I could not understand the query using the available data."
        }

    # 2️⃣ Execute SQL
    raw_data = run_query(sql)
    data = normalize_data(raw_data)

    # 3️⃣ Generate Natural Language Answer
    nl_answer = generate_nl_answer(
        user_query=user_query,
        sql=sql,
        data=data
    )

    return {
        "answer": nl_answer,
        "sql": sql,
        "data": data
    }
