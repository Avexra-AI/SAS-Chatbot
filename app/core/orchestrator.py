# app/core/orchestrator.py

from threading import Lock, Event
import hashlib

from app.core.semantic import SemanticLayer
from app.core.visualization import select_visualization
from app.services.llm import generate_sql, generate_nl_answer
from app.db.session import run_query
from app.utils.serialization import normalize_data
from app.utils.sql_cleaner import clean_sql


semantic = SemanticLayer()

# In-memory request coalescing (per-process)
_in_flight_requests = {}
_in_flight_lock = Lock()


def _get_request_key(user_query: str) -> str:
    normalized = user_query.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def handle_query(user_query: str):
    request_key = _get_request_key(user_query)

    with _in_flight_lock:
        entry = _in_flight_requests.get(request_key)
        if entry:
            event = entry["event"]
        else:
            entry = {
                "event": Event(),
                "result": None,
                "error": None,
            }
            _in_flight_requests[request_key] = entry
            event = None

    # 🕒 Waiter path
    if event:
        event.wait()
        return entry["result"]

    try:
        sql = generate_sql(
            user_query=user_query,
            semantic_layer=semantic.layer
        )

        if not sql:
            entry["result"] = {
                "answer": "I could not answer this question using the available data.",
                "confidence": 0.2
            }
            return entry["result"]

        sql = clean_sql(sql)

        if not sql.lower().strip().startswith("select"):
            entry["result"] = {
                "answer": "Only read-only analytical queries are supported.",
                "sql": sql,
                "confidence": 0.1
            }
            return entry["result"]

        raw_data = run_query(sql)
        data = normalize_data(raw_data)
        visualization = select_visualization(data)

        nl_answer = generate_nl_answer(
            user_query=user_query,
            sql=sql,
            data=data
        )

        confidence = 0.6
        if data:
            confidence += 0.2
        if visualization.get("type") not in ["table", "empty"]:
            confidence += 0.1
        if len(data) <= 10:
            confidence += 0.1

        confidence = min(confidence, 0.95)

        entry["result"] = {
            "answer": nl_answer,
            "visualization": visualization,
            "data": data,
            "sql": sql,
            "confidence": confidence
        }

        return entry["result"]

    except Exception as e:
        entry["result"] = {
            "answer": "There was an error executing the query on the database.",
            "error": str(e),
            "confidence": 0.1
        }
        return entry["result"]

    finally:
        entry["event"].set()
        with _in_flight_lock:
            _in_flight_requests.pop(request_key, None)