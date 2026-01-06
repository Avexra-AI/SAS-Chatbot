# 📊 Sales Analytics – Final Data & Semantic Layer Design

This document explains the **final database tables**, their **relationship**, and the **semantic layer** used for analytics, NL→SQL, and dashboards.

---

## 1. Final Database Tables (Analytical Layer)

After ingesting and preserving raw data, the system exposes **two final analytical tables**.
These tables are **stable, query-ready**, and are the **only tables used by the semantic layer**.

---

### 🔹 Table 1: `sales_line_items`

**Purpose:**
Stores **product-level (line-item) sales data**.
Each row represents **one product sold in an invoice**.

**Schema:**

```sql
sales_line_items (
    line_id        BIGSERIAL PRIMARY KEY,
    date           DATE,
    voucher_no     TEXT NOT NULL,
    firm           TEXT,
    gstin          TEXT,
    product_name   TEXT,
    brand          TEXT,
    category       TEXT,
    sub_category   TEXT,
    quantity       INTEGER,
    rate           NUMERIC(12,2),
    value          NUMERIC(14,2),
    client_type    TEXT
)
```

**Grain:**
➡️ One row = **one product in one invoice**

**Key points:**

* `line_id` is a system-generated primary key
* `voucher_no` links this table to invoice-level data
* No aggregations are performed here
* `client_type` is a physical column (not calculated in semantic layer)

---

### 🔹 Table 2: `sales_transactions`

**Purpose:**
Stores **invoice-level (transaction-level) data**.
Each row represents **one complete invoice**.

**Schema:**

```sql
sales_transactions (
    voucher_no     TEXT PRIMARY KEY,
    date           DATE,
    firm           TEXT,
    gstin          TEXT,
    total_quantity INTEGER,
    net_value      NUMERIC(14,2),
    total_tax      NUMERIC(14,2),
    gross_total    NUMERIC(14,2)
)
```

**Grain:**
➡️ One row = **one invoice**

**Key points:**

* `voucher_no` uniquely identifies an invoice
* Aggregations (quantity, value, tax) are precomputed
* Designed for fast analytics and reporting

---

## 2. Relationship Between Tables

```text
sales_transactions (1) ──── voucher_no ──── (many) sales_line_items
```

**Relationship type:**

* **ONE_TO_MANY**

**Join condition:**

```sql
sales_transactions.voucher_no = sales_line_items.voucher_no
```

**Design rule:**

* Only `voucher_no` is allowed for joins
* Prevents incorrect or AI-inferred joins
* Preserves invoice integrity

---

## 3. Semantic Layer Overview

The semantic layer provides a **business-friendly abstraction** over the final tables.
It is used by:

* NL → SQL systems
* Chatbots
* Dashboards
* Analytics APIs

### 🔹 Models Defined

#### `sales_line_items`

* Maps directly to `sales_line_items` table
* Primary key: `line_id`
* Used for:

  * Product demand
  * Category analysis
  * Client-type based sales

#### `sales_transactions`

* Maps directly to `sales_transactions` table
* Primary key: `voucher_no`
* Used for:

  * Revenue analysis
  * Client purchase frequency
  * Invoice-level trends

---

### 🔹 Metrics Defined

| Metric Name                 | Base Table         | Meaning                        |
| --------------------------- | ------------------ | ------------------------------ |
| `total_sales_value`         | sales_line_items   | Net sales value                |
| `product_demand`            | sales_line_items   | Units sold per product         |
| `client_purchase_frequency` | sales_transactions | Number of purchases per client |
| `gross_revenue`             | sales_transactions | Total billed revenue           |

All metrics:

* Are **human-defined**
* Use **explicit SQL expressions**
* Do **not infer joins automatically**

---

## 4. Architectural Principles Followed

* Raw data is preserved separately (audit-safe)
* Semantic layer never queries raw tables directly
* Final tables are deterministic and refreshable
* No AI-inferred joins or calculations
* Designed for production-scale analytics

---


This design is **implementation-ready** and should not be structurally modified further.
Future changes should be limited to **new metrics or new dimensions**, not schema redesign.
