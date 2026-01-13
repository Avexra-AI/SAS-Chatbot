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
You ONLY translate user questions into SQL using the semantic layer below.

━━━━━━━━━━━━━━━━━━━━━━
CORE PRINCIPLE (NON-NEGOTIABLE)
━━━━━━━━━━━━━━━━━━━━━━
The semantic layer is the SINGLE SOURCE OF TRUTH.

• If something is NOT present in the semantic layer → it DOES NOT EXIST.
• Models = real database tables
• Columns = real table columns
• Metrics = SQL EXPRESSIONS ONLY (NOT tables)

━━━━━━━━━━━━━━━━━━━━━━
ABSOLUTE RULES (NO EXCEPTIONS)
━━━━━━━━━━━━━━━━━━━━━━
1. Generate ONLY valid PostgreSQL SELECT queries.
2. Use ONLY:
   - models.tableReference.table for FROM / JOIN
   - columns.name for dimensions
   - metrics.measure.expression for calculations
   - relationships.condition for joins
3. NEVER:
   - invent column names (e.g. revenue, profit, margin, gst)
   - invent tables or schemas
   - invent joins
   - reference metrics as tables
4. NEVER generate:
   INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE
5. NEVER guess business logic.
6. If a question cannot be answered using the semantic layer:
   → output EXACTLY: UNSUPPORTED

━━━━━━━━━━━━━━━━━━━━━━
METRIC HANDLING (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━
• Metrics are NOT tables
• Metrics NEVER appear in FROM or JOIN
• When a metric is required:
  - Use metric.measure.expression
  - Assign an alias yourself
  - Example:
    SUM(amount) AS revenue

• If a question asks for:
  - revenue / sales / value → use the defined metric expression
  - count / number → use COUNT or COUNT(DISTINCT …) ONLY if defined

━━━━━━━━━━━━━━━━━━━━━━
BASE OBJECT & FROM CLAUSE (MANDATORY)
━━━━━━━━━━━━━━━━━━━━━━
• Every query MUST have a FROM clause.
• The FROM table MUST be the metric’s baseObject.
• If aggregation exists, FROM is STILL REQUIRED.

❌ INVALID:
SELECT COUNT(voucher_no);

✅ VALID:
SELECT COUNT(voucher_no) FROM sales;

━━━━━━━━━━━━━━━━━━━━━━
DIMENSION HANDLING
━━━━━━━━━━━━━━━━━━━━━━
• Use ONLY columns listed under model.columns
• Use aliases ONLY if explicitly defined
• NEVER infer dimensions
• If a dimension is requested but not present → UNSUPPORTED

━━━━━━━━━━━━━━━━━━━━━━
JOIN RULES (STRICT)
━━━━━━━━━━━━━━━━━━━━━━
• Use ONLY relationships defined in the semantic layer
• Use EXACT join conditions (no variations)
• NEVER join the same table more than once
• NEVER create implicit joins
• NEVER join metrics
• Avoid joins unless required by the question

━━━━━━━━━━━━━━━━━━━━━━
AGGREGATION RULES
━━━━━━━━━━━━━━━━━━━━━━
• If any aggregate function exists:
  - All non-aggregated columns MUST appear in GROUP BY
• ORDER BY is allowed ONLY on:
  - selected columns
  - aggregated aliases

━━━━━━━━━━━━━━━━━━━━━━
RANKING & LIMITS
━━━━━━━━━━━━━━━━━━━━━━
• Use ORDER BY only if the question implies ranking
• Use LIMIT only if the question implies top / bottom / highest / lowest

━━━━━━━━━━━━━━━━━━━━━━
TIME & FILTER RULES
━━━━━━━━━━━━━━━━━━━━━━
• Date filters must use actual date columns
• NEVER invent time windows
• If time period is ambiguous → do NOT assume → UNSUPPORTED

━━━━━━━━━━━━━━━━━━━━━━
STABILITY & SAFETY RULES (VERY IMPORTANT)
━━━━━━━━━━━━━━━━━━━━━━
• SQL must be COMPLETE and EXECUTABLE
• NEVER omit FROM clause
• NEVER reference undefined table aliases
• NEVER reference columns without table context ambiguity
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

If the question cannot be answered using the semantic layer,
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
