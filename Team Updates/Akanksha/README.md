# Tally ERP → XML → SQL Data Pipeline

This repository contains an **end-to-end data ingestion pipeline** that converts raw accounting data exported from **Tally Prime** into a **clean, normalized SQL database**, suitable for analytics, NL2SQL, and agentic AI systems.

The work focuses on **data correctness and reproducibility**, not UI or dashboards.

---

## 🚩 Problem
Tally ERP exports data in **legacy XML** that:
- contains illegal XML control characters
- breaks standard XML parsers
- is not directly usable for databases or AI systems

Naively parsing this data leads to **corrupt financial reasoning**.

---

## ✅ Solution
This pipeline:
1. Sanitizes malformed Tally XML
2. Parses vouchers safely
3. Normalizes **ledger-level Debit / Credit entries**
4. Stores atomic accounting data in SQL

---

## 🔧 Pipeline Flow

