# Semantic Layer (MDL) – SAS Sales Intelligence System

## Overview

This repository contains the **Semantic Layer (MDL – Model Definition Layer)** used in the SAS Sales Intelligence project.
The semantic layer acts as a **governed interface between raw sales data and AI-driven analytics**, ensuring that all insights, visualizations, and chatbot responses are **business-aligned, consistent, and reliable**.

The semantic layer prevents AI systems from guessing joins, metrics, or business logic by explicitly defining them in a machine-readable contract.

---

## Why a Semantic Layer?

Traditional AI or Text-to-SQL systems often fail because:

* Business logic is implicit
* Metrics are redefined inconsistently
* Joins are inferred incorrectly
* Results change across dashboards and queries

This semantic layer solves those problems by enforcing:

* **Human-defined business rules**
* **Explicit data relationships**
* **Single source of truth for metrics**

---

## Design Principles

The semantic layer strictly follows these principles:

1. **Business Alignment**

   * All metrics represent real business concepts (sales, demand, revenue, client behavior)
   * No technical or ambiguous definitions are exposed to AI

2. **Data Consistency & Governance**

   * Metrics are defined once and reused everywhere
   * Joins are explicitly declared
   * Business rules are deterministic, not inferred

3. **Technical Architecture & Performance**

   * Aggregations are executed at the database level
   * Clear separation of data grain (line-level vs invoice-level)
   * Optimizer-friendly SQL generation

4. **Iterative Development & Adoption**

   * Versioned semantic contract
   * Phase-based rollout
   * Designed to support future extensions (RBAC, vector search, knowledge graphs)

---

## Data Models (Schema)

### 1. `sales_line_items`

**Grain:** Product-level transaction (line item)

Represents individual products sold in each invoice.

Key fields:

* Product details: `product_name`, `brand`, `category`, `sub_category`
* Transaction details: `date`, `voucher_no`, `firm`
* Quantitative fields: `quantity`, `rate`, `value`
* Derived business field:

  * `client_type`

    * Rule: GST present → `Dealer`, otherwise `End Client`

This table powers **product demand, movement analysis, and category-level insights**.

---

### 2. `sales_transactions`

**Grain:** Invoice-level transaction

Represents aggregated sales at the invoice level.

Key fields:

* Invoice identifiers: `voucher_no`, `date`
* Client information: `firm`, `gstin`
* Financial values: `net_value`, `total_tax`, `gross_total`

This table powers **revenue analysis and client purchase behavior**.

---

## Relationships (Joins)

Only **one explicit relationship** is allowed:

* `sales_transactions.voucher_no = sales_line_items.voucher_no`
* Join type: `ONE_TO_MANY`

No joins on client name, date, or product name are permitted.
This preserves invoice integrity and prevents incorrect aggregations.

---

## Metrics (Business Logic)

All metrics are **human-defined** and cannot be altered or inferred by AI.

### Core Metrics

* **Total Sales Value**
  `SUM(value)`
  Net sales before tax

* **Product Demand**
  `SUM(quantity)`
  Measures product movement by volume

* **Client Purchase Frequency**
  `COUNT(DISTINCT voucher_no)`
  Tracks repeat vs one-time buyers

* **Gross Revenue**
  `SUM(gross_total)`
  Final billed revenue including tax

### Time Analysis

Metrics support controlled time grains:

* Year
* Quarter
* Month

This enables trend analysis without exposing raw date logic to AI.

---

## Governance & Versioning

The semantic layer includes explicit governance metadata:

* Versioned (`v1.0`)
* Phase-defined (Phase-1: Text-to-SQL + Analytics)
* Clear business domain declaration
* Future extension roadmap documented

This ensures safe evolution without breaking dashboards or AI behavior.

---

## How This Is Used

This semantic layer is consumed by:

* AI chatbots (Text-to-SQL)
* Analytics dashboards
* Visualization pinning workflows
* Future intelligent agents

It acts as the **single source of truth** for all analytical outputs.

---

## Key Guarantee

With this semantic layer in place:

* AI cannot hallucinate joins
* AI cannot redefine metrics
* Dashboards and chatbot answers always stay consistent
* Business users receive trustworthy insights

---

## Future Extensions (Planned)

* Vector-based synonym handling
* Role-based access control
* Knowledge graph relationships
* Metric-level caching

---
