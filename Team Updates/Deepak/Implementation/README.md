# Backend Architecture (Chatbot and Dashboard Only)

<img width="257" height="375" alt="image" src="https://github.com/user-attachments/assets/10a08915-e560-446c-a914-b89c30d19514" />

## Project Structure

```text
backend/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Env & settings
│   ├── dependencies.py         # DB, auth, cache deps
│   │
│   ├── api/                    # HTTP layer (thin)
│   │   ├── router.py
│   │   ├── chat.py             # Chatbot endpoint
│   │   ├── dashboard.py        # Dashboard data APIs
│   │   └── health.py
│   │
│   ├── core/                   # SYSTEM BRAIN
│   │   ├── orchestrator.py     # End-to-end flow controller
│   │   ├── intent.py           # LLM intent extraction
│   │   ├── semantic.py         # Metric/dimension validation
│   │   ├── nl2sql.py           # Deterministic SQL builder
│   │   ├── visualization.py    # Chart selector logic
│   │   ├── cache.py            # Semantic & response cache
│   │   └── fallback.py         # Low-confidence / failure handling
│   │
│   ├── db/
│   │   ├── session.py          # Neon DB connection
│   │   ├── models.py           # ORM models (sales, products, etc.)
│   │   └── queries.py          # Approved SQL templates only
│   │
│   ├── services/
│   │   └── llm.py              # LLM abstraction (OpenAI/Groq/etc.)
│   │
│   ├── schemas/
│   │   ├── chat.py             # Chat request/response schemas
│   │   └── dashboard.py        # Visualization schemas
│   │
│   └── utils/
│       ├── logging.py
│       ├── security.py
│       └── validators.py
│
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt


```

