# Backend Architecture (Chatbot and Dashboard Only)

---

## Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   │
│   ├── api/
│   │   ├── router.py
│   │   ├── chat.py
│   │   ├── dashboard.py
│   │   └── health.py
│   │
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── intent.py
│   │   ├── semantic.py
│   │   ├── nl2sql.py
│   │   ├── rag.py
│   │   ├── cache.py
│   │   └── fallback.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   ├── models.py
│   │   ├── queries.py
│   │   └── migrations/
│   │
│   ├── services/
│   │   ├── llm.py
│   │   └── embeddings.py
│   │
│   ├── schemas/
│   │   ├── chat.py
│   │   └── dashboard.py
│   │
│   └── utils/
│       ├── logging.py
│       ├── security.py
│       └── validators.py
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

```
---
