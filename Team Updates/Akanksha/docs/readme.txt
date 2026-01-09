Tally Live Sync Agent
Technical Documentation & Execution Flow
1. Purpose of This Module (Context First)

This module is a local data ingestion and preprocessing component inside a larger AgentX AI system.
Its responsibility is ONLY ONE THING:
Convert live, continuously changing Tally accounting data into a clean, normalized, always-updated local dataset that downstream systems (dashboards / AI agents) can safely consume.

It does not:

predict
visualize
expose APIs
modify Tally data
This strict separation is intentional and correct


┌────────────────────┐
│  Tally Prime ERP   │
│ (Live Company Data)│
└─────────┬──────────┘
          │  HTTP XML (Read-only)
          ▼
┌────────────────────┐
│ Tally Source Layer │
│ (XML Fetch)        │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ XML Sanitizer      │
│ (Fix malformed XML)│
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Normalizer         │
│ (Voucher → Ledger) │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Local Store        │
│ (SQLite Live DB)   │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ AgentX AI /        │
│ Dashboard Layer    │
└────────────────────┘

step :2 code
2.1
agent.py — The Orchestrator (Main Loop)

Role:
Acts as the brain of the sync process.
Key responsibilities:
Load last sync state
Trigger incremental fetch
Coordinate sanitization, normalization, and storage
Ensure idempotency (no duplicate corruption)
Run continuously

2.2tally_source.py — Tally Connector

Role:
Handles only communication with Tally Prime.
What it does:
Sends an XML request to Tally’s HTTP server
Requests Day Book data for a specific date range
Receives raw ERP XML response
What it deliberately avoids:
No parsing
No business logic
No state tracking
Why this separation matters:
If Tally’s interface changes, only this file needs modification.


2.3xml_sanitizer.py — ERP XML Cleanup Layer

Problem it solves:
Tally often emits invalid XML characters (control chars, broken entities) that crash standard XML parsers.

What it does:
Removes illegal ASCII control characters
Strips malformed character references
Produces parser-safe XML text

Why this is critical:
Without this step:
The entire pipeline would fail on a single bad voucher
AI systems downstream would never see consistent data
This layer is non-negotiable in real ERP environments.




2.3normalizer.py — Accounting-Aware Transformation

Role:
Transforms ERP-specific structures into analytics-friendly records.

Key transformations:
Voucher → multiple ledger entries
Amount sign → DR / CR semantics
Voucher fingerprint generation
fingerprint = hash(
    voucher_no +
    voucher_date +
    voucher_type +
    ledger_entries
)

2.4store.py — Local Live Dataset

Role:
Maintains the single source of truth for downstream systems.

Design choices:
SQLite (local, simple, reliable)
Voucher table (metadata)
Ledger entry table (facts)
Why local storage is correct here:
No cloud dependency

Works on company machines
Dashboards / AI can query without touching Tally

2.5state.py — Incremental Sync Memory

Role:
Tracks what has already been processed.

Stores:
Last sync date
Fingerprints of processed vouchers
Why this exists:
Without state:
Every cycle would reprocess everything
Data duplication would explode
Performance would degrade rapidly

step:3...
Runtime Behavior (Step-by-Step)
One Full Sync Cycle

Agent starts:
Loads previous sync state
Requests incremental Day Book data from Tally
Sanitizes malformed XML
Parses vouchers
Generates fingerprints
Filters already-processed vouchers
Inserts new data into local DB
Updates sync state
Sleeps and repeats
  
step4:Why This Works With “Live” Company Data

Important clarification:
Tally does NOT provide push-based real-time streams
Industry-standard approach is polling-based near-real-time sync

This agent:
polls frequently
pulls only deltas
keeps the dataset continuously fresh

step 5:
