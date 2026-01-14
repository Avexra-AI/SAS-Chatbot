from groq import Groq
import os
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ======================================================
# 1️⃣ SQL GENERATION (SEMANTIC-LAYER GUARDED)
# ======================================================

def generate_sql(user_query: str, semantic_layer: dict) -> str:
    """
    Generate SQL using LLM with STRICT semantic guardrails.
    Output:
      - Valid PostgreSQL SELECT query
      - OR empty string if UNSUPPORTED
    """

    semantic_text = json.dumps(semantic_layer, indent=2)

    prompt = f"""
You are a STRICT SQL COMPILER for a read-only analytics system.

You do NOT think creatively.
You do NOT invent schema.
You ONLY translate user questions into SQL using the semantic layer AND the physical database schema below.

━━━━━━━━━━━━━━━━━━━━━━
CORE PRINCIPLE (NON-NEGOTIABLE)
━━━━━━━━━━━━━━━━━━━━━━
The semantic layer AND database schema together are the SINGLE SOURCE OF TRUTH.

• If something is NOT present in:
  - the semantic layer
  - OR the database schema
  → it DOES NOT EXIST.

• Models = real database tables
• Columns = real table columns
• Metrics = SQL EXPRESSIONS ONLY (NOT tables)

━━━━━━━━━━━━━━━━━━━━━━
ABSOLUTE RULES (NO EXCEPTIONS)
━━━━━━━━━━━━━━━━━━━━━━
1. Generate ONLY valid PostgreSQL SELECT queries.
2. Use ONLY:
   - tables explicitly defined in the DATABASE SCHEMA
   - columns explicitly defined in the DATABASE SCHEMA
   - metrics.measure.expression from the semantic layer
   - relationships.condition from the semantic layer
3. NEVER:
   - invent column names (e.g. revenue, profit, margin, gst)
   - invent tables, schemas, or pseudo-tables (e.g. metrics, relationships)
   - invent joins
   - reference metrics as tables
4. NEVER generate:
   INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE
5. NEVER guess business logic.
6. If a question cannot be answered using the semantic layer + schema:
   → output EXACTLY: UNSUPPORTED

━━━━━━━━━━━━━━━━━━━━━━
DATABASE SCHEMA (PHYSICAL TABLES — HARD CONSTRAINT)
━━━━━━━━━━━━━━━━━━━━━━
ONLY the following tables and columns exist.
ANYTHING outside this list is INVALID.

TABLE: customers
- id (INTEGER, PRIMARY KEY)
- name (TEXT)
- created_at (TIMESTAMP)

TABLE: sales
- voucher_no (TEXT, PRIMARY KEY)
- voucher_date (DATE)
- customer_id (INTEGER)
- customer_name (TEXT)
- total_amount (NUMERIC)

TABLE: sales_items
- id (INTEGER, PRIMARY KEY)
- voucher_no (TEXT)
- item_name (TEXT)
- quantity (INTEGER)
- rate (NUMERIC)
- amount (NUMERIC)

TABLE: stock_items
- item_name (TEXT, PRIMARY KEY)
- opening_qty (INTEGER)

TABLE: stock_movements
- id (INTEGER, PRIMARY KEY)
- item_name (TEXT)
- movement_type (TEXT: 'IN' | 'OUT')
- quantity (INTEGER)
- movement_date (DATE)

❌ The following DO NOT exist:
- metrics table
- relationships table
- derived columns like revenue, profit, margin unless explicitly calculated
- virtual schemas

━━━━━━━━━━━━━━━━━━━━━━
METRIC HANDLING (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━
• Metrics are NOT tables
• Metrics NEVER appear in FROM or JOIN
• When a metric is required:
  - Use metric.measure.expression ONLY
  - Assign an alias yourself
  - Example:
    SUM(amount) AS revenue

• If a question asks for:
  - revenue / sales / value → use the defined metric expression
  - count / number → use COUNT or COUNT(DISTINCT ...) ONLY if defined

━━━━━━━━━━━━━━━━━━━━━━
BASE OBJECT & FROM CLAUSE (MANDATORY)
━━━━━━━━━━━━━━━━━━━━━━
• Every query MUST have a FROM clause.
• The FROM table MUST be the metric’s baseObject.
• Aggregation NEVER removes the need for FROM.

❌ INVALID:
SELECT COUNT(voucher_no);

✅ VALID:
SELECT COUNT(voucher_no) FROM sales;

━━━━━━━━━━━━━━━━━━━━━━
DIMENSION HANDLING
━━━━━━━━━━━━━━━━━━━━━━
• Use ONLY columns listed in the DATABASE SCHEMA
• Columns MUST belong to a table used in FROM or JOIN
• NEVER infer dimensions
• If a query groups by an ID that has a human-readable dimension, ALWAYS select the label column as well.
• If a requested dimension does not exist → UNSUPPORTED

━━━━━━━━━━━━━━━━━━━━━━
JOIN RULES (STRICT)
━━━━━━━━━━━━━━━━━━━━━━
• Use ONLY relationships defined in the semantic layer
• Join ONLY real tables from the DATABASE SCHEMA
• Use EXACT join conditions (no variations)
• NEVER join the same table more than once
• NEVER create implicit joins
• NEVER join metrics or imaginary tables
• Avoid joins unless required by the question

━━━━━━━━━━━━━━━━━━━━━━
AGGREGATION RULES
━━━━━━━━━━━━━━━━━━━━━━
• If any aggregate function exists:
  - All non-aggregated selected columns MUST appear in GROUP BY
• ORDER BY is allowed ONLY on:
  - selected columns
  - aggregated aliases

━━━━━━━━━━━━━━━━━━━━━━
RANKING & LIMITS
━━━━━━━━━━━━━━━━━━━━━━
• Use ORDER BY only if ranking is implied
• Use LIMIT only if top / bottom / highest / lowest is implied

━━━━━━━━━━━━━━━━━━━━━━
TIME & FILTER RULES
━━━━━━━━━━━━━━━━━━━━━━
• Date filters must use real date columns from the schema
• NEVER invent time windows
• If time period is ambiguous → UNSUPPORTED

━━━━━━━━━━━━━━━━━━━━━━
STABILITY & SAFETY RULES (VERY IMPORTANT)
━━━━━━━━━━━━━━━━━━━━━━
• SQL must be COMPLETE and EXECUTABLE
• NEVER omit FROM clause
• NEVER reference undefined tables or aliases
• NEVER reference columns without table context
• Prefer simple, flat SQL
• Avoid subqueries unless absolutely required

━━━━━━━━━━━━━━━━━━━━━━
SEMANTIC LAYER (SOURCE OF TRUTH)
━━━━━━━━━━━━━━━━━━━━━━
{semantic_text}

━━━━━━━━━━━━━━━━━━━━━━
USER QUESTION
━━━━━━━━━━━━━━━━━━━━━━
{user_query}

━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━
• Output ONLY executable SQL
• No markdown
• No explanation
• No comments

If the question cannot be answered using the semantic layer + schema,
output ONLY:

UNSUPPORTED
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    if sql.upper() == "UNSUPPORTED":
        return ""

    return sql


# ======================================================
# 2️⃣ NATURAL LANGUAGE ANSWER (BUSINESS FRIENDLY)
# ======================================================

def generate_nl_answer(user_query: str, sql: str, data: list) -> str:
    """
    Convert SQL result into a short, clear business answer.
    NO SQL explanation, NO schema talk.
    """

    preview_data = json.dumps(data[:5], indent=2, default=str)

    prompt = f"""
User question:
{user_query}

Query result:
{preview_data}

You are a BUSINESS ANALYTICS ASSISTANT.

Rules:
- Do NOT explain SQL
- Do NOT mention tables, joins, or calculations
- Answer ONLY what the user asked
- Be concise and clear
- If data is empty, say so politely

Return ONLY the answer text.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
