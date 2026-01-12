# app/core/cache.py

import os
import json
import hashlib
from typing import Optional

# =========================
# ENV
# =========================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "semantic-cache")

USE_PINECONE = bool(PINECONE_API_KEY)

# =========================
# INIT PINECONE (OPTIONAL)
# =========================
if USE_PINECONE:
    from pinecone import Pinecone

    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if not exists
    existing_indexes = pc.list_indexes().names()
    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=8,  # dummy dimension (we store metadata, not vectors)
            metric="cosine",
            spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
        )

    index = pc.Index(PINECONE_INDEX_NAME)
else:
    index = None


# =========================
# UTILS
# =========================
def _hash_key(data: dict) -> str:
    """
    Stable hash for semantic intent
    (metric + dimensions + filters)
    """
    raw = json.dumps(data, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


# =========================
# CACHE: GET
# =========================
def get_from_cache(intent: dict) -> Optional[dict]:
    """
    intent example:
    {
        "metric": "total_sales_amount",
        "dimensions": ["customer"],
        "filters": {}
    }
    """
    if not index:
        return None

    key = _hash_key(intent)

    try:
        res = index.fetch(ids=[key])
        if key in res.vectors:
            return json.loads(res.vectors[key].metadata["response"])
    except Exception:
        return None

    return None


# =========================
# CACHE: STORE
# =========================
def store_in_cache(intent: dict, response: dict):
    if not index:
        return

    key = _hash_key(intent)

    index.upsert([
        {
            "id": key,
            "values": [0.0] * 8,  # dummy vector
            "metadata": {
                "response": json.dumps(response)
            }
        }
    ])
