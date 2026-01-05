# Backend Architecture – Avexra AI

This backend follows a **modular monolith architecture** designed to be **secure, scalable, production-ready**, and **cost-efficient**.
It supports **AI-powered analytics**, including **NL → SQL**, **RAG**, **semantic validation**, **dashboarding**, and **automated data ingestion** using **Neon PostgreSQL**.

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
│   │   ├── upload.py
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
│   ├── agents/
│   │   └── data_agent.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   ├── models.py
│   │   ├── queries.py
│   │   └── migrations/
│   │
│   ├── services/
│   │   ├── llm.py
│   │   ├── embeddings.py
│   │   └── storage.py
│   │
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── dashboard.py
│   │   └── upload.py
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

## Root Level Files

### `Dockerfile`

Defines how the backend is containerized for deployment.
Includes:

* Python runtime
* Dependency installation
* Application startup command

Used for production and staging deployments.

---

### `docker-compose.yml`

Used for local development and testing.
Typically orchestrates:

* Backend service
* Redis (cache)
* Optional worker services

---

### `requirements.txt`

Lists all Python dependencies required by the backend, including:

* FastAPI
* SQLAlchemy
* Pydantic
* LLM SDKs
* Database drivers
* Caching libraries

---

### `README.md`

This documentation file.
Explains architecture, structure, and responsibilities of each component.

---

## `app/` – Application Core

This folder contains the entire backend application logic.

---

### `app/main.py`

**Entry point of the application**

Responsibilities:

* Create FastAPI app instance
* Register middleware (CORS, logging, auth)
* Include API routers
* Application startup and shutdown events

This file should remain **small and declarative**.

---

### `app/config.py`

**Centralized configuration management**

Responsibilities:

* Load environment variables
* Define settings (DB URL, API keys, cache config)
* Handle environment-specific configuration (dev, prod)

Acts as the single source of truth for configuration.

---

### `app/dependencies.py`

**Shared dependency injection layer**

Responsibilities:

* Database session providers
* Authentication dependencies
* Cache clients (Redis)
* Common reusable dependencies for routes

Used heavily by the API layer.

---

## `app/api/` – HTTP Interface Layer (Thin Layer)

This layer exposes REST endpoints.
**No business logic is implemented here.**

---

### `router.py`

Registers and combines all API routes into a single router.

Example:

* `/chat`
* `/dashboard`
* `/upload`
* `/health`

---

### `chat.py`

Handles chatbot-related HTTP requests.

Responsibilities:

* Accept user queries
* Validate request payload
* Call the core orchestrator
* Return chatbot responses

No AI or SQL logic exists here.

---

### `dashboard.py`

Manages dashboard-related endpoints.

Responsibilities:

* Fetch pinned insights
* Save dashboard layouts
* Serve dashboard configurations to frontend

---

### `upload.py`

Handles data upload endpoints.

Responsibilities:

* Accept raw files (CSV, Excel)
* Validate file metadata
* Trigger the data ingestion agent asynchronously

---

### `health.py`

Health check endpoint.

Used by:

* Load balancers
* Monitoring systems
* Deployment health checks

---

## `app/core/` – Business Logic (System Brain)

This is the **most critical layer** of the backend.

---

### `orchestrator.py`

**Central decision-making engine**

Responsibilities:

* Control end-to-end chatbot flow
* Coordinate intent detection, semantic validation, caching, and execution
* Decide whether to use NL→SQL, RAG, or fallback

Every chatbot query passes through this file.

---

### `intent.py`

**Intent detection and classification**

Responsibilities:

* Determine what the user wants (KPI, trend, comparison, explanation)
* Assign confidence scores
* Route queries appropriately

---

### `semantic.py`

**Semantic validation and safety layer**

Responsibilities:

* Validate metrics, dimensions, and filters
* Enforce schema awareness
* Prevent unsafe or ambiguous queries
* Normalize queries into structured representations

Critical for security and correctness.

---

### `nl2sql.py`

**Natural Language to SQL translation**

Responsibilities:

* Convert structured semantic queries into SQL
* Use templates and whitelisting
* Enforce read-only queries
* Estimate query cost and complexity

LLMs never directly execute SQL.

---

### `rag.py`

**Retrieval Augmented Generation logic**

Responsibilities:

* Retrieve contextual documents or summaries
* Construct prompts with retrieved context
* Generate grounded explanations

Used only for explanatory or contextual answers.

---

### `cache.py`

**Caching and performance optimization**

Responsibilities:

* Semantic caching of responses
* Request coalescing
* TTL and invalidation logic
* Reduce LLM and DB load

---

### `fallback.py`

**Resilience and cost control**

Responsibilities:

* Model fallback logic
* Frugal cascade (cheap → expensive models)
* Partial response handling
* Graceful degradation

Ensures system never fails silently.

---

## `app/agents/` – Autonomous Workers

---

### `data_agent.py`

**Automated data ingestion agent**

Responsibilities:

* Parse uploaded files
* Clean and normalize data
* Apply business rules (e.g., GST → client type)
* Write structured data to Neon DB
* Handle versioning and metadata

Runs asynchronously, isolated from request flow.

---

## `app/db/` – Database Layer

All database-related logic lives here.

---

### `session.py`

Manages database connections and sessions.

Responsibilities:

* Create Neon DB connections
* Handle read/write separation
* Provide session lifecycle management

---

### `models.py`

Defines database models using ORM.

Responsibilities:

* Tables for sales data
* Dashboard metadata
* User configurations
* Insight storage

---

### `queries.py`

**Centralized SQL access layer**

Responsibilities:

* All raw SQL queries
* Optimized analytics queries
* Pre-aggregated query logic

No SQL is allowed outside this file.

---

### `migrations/`

Database migration scripts.

Used for:

* Schema evolution
* Versioned database changes
* Production-safe updates

---

## `app/services/` – External Integrations

---

### `llm.py`

Handles communication with LLM providers.

Responsibilities:

* Model selection
* Prompt execution
* Cost tracking
* Provider abstraction

Allows easy switching between providers.

---

### `embeddings.py`

Manages embedding generation.

Responsibilities:

* Generate embeddings
* Interface with vector storage
* Support semantic search and RAG

---

### `storage.py`

Handles external file storage.

Responsibilities:

* Upload raw files
* Generate signed URLs
* Manage file lifecycle

---

## `app/schemas/` – API Contracts

Defines Pydantic models for request and response validation.

---

### `chat.py`

Schemas for chatbot requests and responses.

---

### `dashboard.py`

Schemas for dashboard layouts and pinned insights.

---

### `upload.py`

Schemas for file upload requests and metadata.

---

## `app/utils/` – Shared Utilities

---

### `logging.py`

Centralized logging configuration.

Responsibilities:

* Structured logs
* Request tracing
* Error logging

---

### `security.py`

Security helpers.

Responsibilities:

* Token validation
* Permission checks
* Encryption utilities

---

### `validators.py`

Reusable validation utilities.

Responsibilities:

* Input sanitization
* Schema checks
* Custom business validations

---

## `tests/`

Contains unit and integration tests.

Covers:

* Core logic
* API endpoints
* Database interactions
* Agent workflows

---

## Architectural Summary

* **Modular monolith** with clear internal boundaries
* Secure access to Neon DB
* Cost-optimized AI workflows
* Production-ready patterns from day one
* Easy transition to microservices in the future

This structure is intentionally designed to stay **clean at scale** while remaining **simple to reason about**.
