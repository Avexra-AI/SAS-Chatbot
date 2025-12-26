import pandas as pd
import os
from pathlib import Path

# ==================================================
# 0. CONFIGURATION (SEPARATE FROM LOGIC)
# ==================================================
BASE_DIR = Path(r"C:\Users\akank\OneDrive\Desktop\AverxaAI\SAS-Chatbot\Team Updates\Akanksha")
INPUT_FILE = BASE_DIR / "DECEMBER SALE.xls"
OUTPUT_DIR = BASE_DIR

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

# ==================================================
# 1. LOAD RAW DATA (SKIP METADATA)
# ==================================================
raw_df = pd.read_excel(INPUT_FILE, header=7)
raw_df.columns = raw_df.columns.str.strip()

# ==================================================
# 2. REMOVE EMBEDDED HEADER ROW
# ==================================================
df = raw_df[raw_df.iloc[:, 1] != "Particulars"].reset_index(drop=True)

# ==================================================
# 3. RENAME COLUMNS (EXPLICIT & FIXED)
# ==================================================
EXPECTED_COLUMNS = [
    "date", "particular", "voucher_type", "voucher_no", "gstin",
    "quantity", "alt_units", "rate", "value", "gross_total",
    "sale_18_local", "cgst_9", "sgst_9", "round_off",
    "sale_18_interstate", "igst_18", "freight"
]

if len(df.columns) != len(EXPECTED_COLUMNS):
    raise ValueError("Column count mismatch. Excel format may have changed.")

df.columns = EXPECTED_COLUMNS

# ==================================================
# 4. DATE NORMALIZATION (FORMAT ONLY)
# ==================================================
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# ==================================================
# 5. REMOVE SUMMARY / GRAND TOTAL ROWS
# ==================================================
df = df[~df["particular"].str.lower().eq("grand total")]

# ==================================================
# 6. FILL-DOWN CONTEXT COLUMNS (AS PER NOTE)
# ==================================================
df["voucher_no"] = df["voucher_no"].ffill()
df["gstin"] = df["gstin"].ffill()
df["date"] = df["date"].ffill()

# ==================================================
# 7. NUMERIC CLEANING (CONTROLLED)
# ==================================================
NUMERIC_COLS = [
    "quantity", "rate", "value", "gross_total",
    "sale_18_local", "sale_18_interstate",
    "cgst_9", "sgst_9", "igst_18", "round_off", "freight"
]

for col in NUMERIC_COLS:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)   # remove thousand separators
        .str.replace(r"[^\d\.-]", "", regex=True)
        .replace("", None)
        .astype(float)
    )

# ==================================================
# 8. IDENTIFY INVOICE ROWS
# ==================================================
df["is_invoice"] = df["gross_total"].notna() & df["voucher_no"].notna()

# ==================================================
# 9. GENERATE INVOICE ID (STABLE)
# ==================================================
df["invoice_id"] = df["voucher_no"]

if df[df["is_invoice"]]["invoice_id"].isna().any():
    raise ValueError("Invoice rows without invoice_id detected")

# ==================================================
# 10. BASIC ENTITY NORMALIZATION
# ==================================================
df["particular"] = (
    df["particular"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# ==================================================
# 11. BUILD INVOICE TABLE
# ==================================================
invoices = (
    df[df["is_invoice"]]
    [[
        "invoice_id", "date", "particular", "voucher_type", "gstin",
        "quantity", "gross_total", "sale_18_local",
        "sale_18_interstate", "cgst_9", "sgst_9",
        "igst_18", "round_off", "freight"
    ]]
    .rename(columns={
        "particular": "firm_name",
        "quantity": "total_quantity"
    })
    .reset_index(drop=True)
)

# ==================================================
# 12. BUILD INVOICE ITEM TABLE
# ==================================================
invoice_items = (
    df[
        (~df["is_invoice"]) &
        (df["quantity"].notna())
    ]
    [[
        "invoice_id", "particular", "quantity", "rate", "value"
    ]]
    .rename(columns={
        "particular": "product_name"
    })
    .reset_index(drop=True)
)

# ==================================================
# 13. HARD ACCOUNTING VALIDATION
# ==================================================
qty_check = (
    invoice_items
    .groupby("invoice_id")["quantity"]
    .sum()
    .reset_index(name="sum_product_qty")
    .merge(
        invoices[["invoice_id", "total_quantity"]],
        on="invoice_id",
        how="left"
    )
)

if not (qty_check["sum_product_qty"] == qty_check["total_quantity"]).all():
    raise ValueError("❌ Quantity mismatch between invoices and items")

# ==================================================
# 14. EXPORT OUTPUTS
# ==================================================
invoices.to_csv(OUTPUT_DIR / "invoices_clean.csv", index=False)
invoice_items.to_csv(OUTPUT_DIR / "invoice_items_clean.csv", index=False)

print("✅ Preprocessing completed successfully (Version 2.0)")
print("Invoices:", invoices.shape)
print("Invoice Items:", invoice_items.shape)
