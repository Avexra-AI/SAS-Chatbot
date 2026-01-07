Tally Live Sync Agent

#Purpose

This module implements a local Tally live synchronization
agent used as a data ingestion layer within the larger AgentX AI system.

Its sole responsibility is to continuously extract, preprocess, and
 maintain an up-to-date accounting dataset from a 
 company’s Tally Prime instance so that downstream components
  (dashboards, analytics, and agentic AI) always operate on fresh data.

  #Role in the Overall System

This module is NOT a complete application.

It acts as the first stage in the AgentX AI pipeline:
Tally Prime (Live Company Data)
        ↓
Tally Live Sync Agent (this module)
        ↓
Clean, Normalized Local Dataset
        ↓
AgentX AI Dashboard & Reasoning Layer


#Scope & Responsibilities
What this module DOES

1.Connects to Tally Prime via its official HTTP/XML interface
2.Pulls incremental accounting data at fixed intervals
3.Sanitizes malformed ERP XML
4.Normalizes vouchers into ledger-level records
5.Maintains a continuously updated local dataset
6.Handles edits and duplicates safely


#Near-Real-Time Data Behavior
This module achieves near-real-time synchronization by:
polling Tally periodically (e.g., every 60 seconds)
fetching only new or modified vouchers
updating the dataset incrementally

tally_live_agent/
│
├── agent.py             # main sync loop
├── tally_source.py      # Tally HTTP connector
├── xml_sanitizer.py     # legacy XML cleanup
├── normalizer.py        # voucher → ledger normalization
├── store.py             # local persistent store
├── state.py             # incremental sync tracking
