# # app/core/orchestrator.py

# from app.core.semantic import SemanticLayer
# from app.services.llm import generate_sql, generate_nl_answer
# from app.db.session import run_query
# from app.utils.serialization import normalize_data
# from app.utils.sql_cleaner import clean_sql


# semantic = SemanticLayer()


# def handle_query(user_query: str):
#     """
#     End-to-end flow:
#     User → LLM (SQL generation) → Semantic guardrails → DB → LLM (NL answer)
#     """

#     # 1️⃣ Generate SQL using LLM + semantic context
#     sql = generate_sql(
#         user_query=user_query,
#         semantic_layer=semantic.layer
#     )

#     if not sql:
#         return {
#             "answer": "I could not understand your query using the available data."
#         }

#     # 2️⃣ Clean SQL (remove ```sql, markdown, etc.)
#     sql = clean_sql(sql)

#     # 3️⃣ Safety guard: allow only SELECT queries
#     if not sql.lower().strip().startswith("select"):
#         return {
#             "answer": "Only read-only analytical queries are supported.",
#             "sql": sql
#         }

#     # 4️⃣ Execute SQL
#     try:
#         raw_data = run_query(sql)
#     except Exception as e:
#         return {
#             "answer": "There was an error executing the query on the database.",
#             "error": str(e),
#             "sql": sql
#         }

#     # 5️⃣ Normalize DB output (Decimal, date, datetime → JSON-safe)
#     data = normalize_data(raw_data)

#     # 6️⃣ Generate Natural Language Answer
#     nl_answer = generate_nl_answer(
#         user_query=user_query,
#         sql=sql,
#         data=data
#     )

#     # 7️⃣ Final response
#     return {
#         "answer": nl_answer,
#         "sql": sql,
#         "data": data
#     }

# app/core/orchestrator.py

from app.core.semantic import SemanticLayer
from app.core.visualization import select_visualization
from app.services.llm import generate_sql, generate_nl_answer
from app.db.session import run_query
from app.utils.serialization import normalize_data
from app.utils.sql_cleaner import clean_sql


semantic = SemanticLayer()


def handle_query(user_query: str):
    """
    End-to-end flow:
    User → LLM (SQL generation with semantic context)
         → SQL safety checks
         → DB execution
         → Visualization selection
         → LLM (natural language answer)
    """

    # 1️⃣ Generate SQL using LLM + semantic layer
    sql = generate_sql(
        user_query=user_query,
        semantic_layer=semantic.layer
    )

    if not sql:
        return {
            "answer": "I could not answer this question using the available data.",
            "confidence": 0.2
        }

    # 2️⃣ Clean SQL
    sql = clean_sql(sql)

    # 3️⃣ Safety guard: read-only
    if not sql.lower().strip().startswith("select"):
        return {
            "answer": "Only read-only analytical queries are supported.",
            "sql": sql,
            "confidence": 0.1
        }

    # 4️⃣ Execute SQL
    try:
        raw_data = run_query(sql)
    except Exception as e:
        return {
            "answer": "There was an error executing the query on the database.",
            "error": str(e),
            "sql": sql,
            "confidence": 0.1
        }

    # 5️⃣ Normalize DB output
    data = normalize_data(raw_data)

    # 6️⃣ Visualization selection (DATA ONLY)
    visualization = select_visualization(data)

    # 7️⃣ Natural language answer
    nl_answer = generate_nl_answer(
        user_query=user_query,
        sql=sql,
        data=data
    )

    # 8️⃣ Confidence scoring
    confidence = 0.6
    if data:
        confidence += 0.2
    if visualization.get("type") not in ["table", "empty"]:
        confidence += 0.1
    if len(data) <= 10:
        confidence += 0.1

    confidence = min(confidence, 0.95)

    # 9️⃣ Final response
    return {
        "answer": nl_answer,
        "visualization": visualization,
        "data": data,
        "sql": sql,
        "confidence": confidence
    }
