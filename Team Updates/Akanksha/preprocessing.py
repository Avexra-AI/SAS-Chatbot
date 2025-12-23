import pandas as pd
import os

# =====================================
# 1. FILE PATH (ABSOLUTE, NO GUESSING)
# =====================================
file_path = r"C:\Users\akank\OneDrive\Desktop\AverxaAI\SAS-Chatbot\Team Updates\Akanksha\DECEMBER SALE.xls"

if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found at: {file_path}")

# =====================================
# 2. READ EXCEL & BASIC CLEANUP
# =====================================
df = pd.read_excel(file_path, skiprows=8)

# clean column names
df.columns = df.columns.str.strip()

print("Initial columns:")
print(df.columns.tolist())
print("Initial shape:", df.shape)

# =====================================
# 3. DROP UNWANTED COLUMNS
# =====================================
cols_to_drop = [
    "SALES @18% Inter-State",
    "IGST @18%",
    "Freight"
]

df = df.drop(columns=cols_to_drop, errors="ignore")

print("\nColumns after dropping:")
print(df.columns.tolist())

# =====================================
# 4. HIERARCHICAL TRANSFORMATION
#    Parent: Firm / Invoice row
#    Child : Product row
# =====================================

# Rule:
# Date NOT NULL  -> Firm / Invoice row
# Date NULL      -> Product row

df["is_firm_row"] = df["Date"].notna()

# Firm name from invoice rows
df["FIRM"] = df["Particulars"].where(df["is_firm_row"])
df["FIRM"] = df["FIRM"].ffill()

# Product name from product rows
df["FIRM_PRODUCT"] = df["Particulars"].where(~df["is_firm_row"])

# Drop helper + old column (semantic cleanup)
df = df.drop(columns=["Particulars", "is_firm_row"])

# =====================================
# 5. REORDER COLUMNS (SAFE)
# =====================================
priority_cols = [
    "Date",
    "FIRM",
    "FIRM_PRODUCT",
    "Voucher Type",
    "Voucher No.",
    "GSTIN/UIN"
]

priority_cols = [c for c in priority_cols if c in df.columns]

df = df[
    priority_cols +
    [col for col in df.columns if col not in priority_cols]
]


# 6. FINAL VERIFICATION VIEW

print("\nFINAL DATA PREVIEW:")
print(df.head(20).to_string(index=False))
print("\nFinal shape:", df.shape)


# 7. SAVE CLEANED DATASET

output_path = r"C:\Users\akank\OneDrive\Desktop\AverxaAI\SAS-Chatbot\Team Updates\Akanksha\cleaned_sales_dataset.xlsx"
df.to_excel(output_path, index=False)

print(f"\nSaved cleaned dataset to:\n{output_path}")


# 8. PRODUCT-ONLY DATASET


product_df = df[df["FIRM_PRODUCT"].notna()].copy()

print("\nPRODUCT-LEVEL DATA PREVIEW:")
print(
    product_df[
        [
            "Date",
            "FIRM",
            "FIRM_PRODUCT",
            "Quantity",
            "Rate",
            "Value"
        ]
    ].head(20).to_string(index=False)
)

print("\nProduct-level shape:", product_df.shape)

product_output_path = r"C:\Users\akank\OneDrive\Desktop\AverxaAI\SAS-Chatbot\Team Updates\Akanksha\product_level_sales.xlsx"

product_df.to_excel(product_output_path, index=False)

print(f"\nSaved product-level dataset to:\n{product_output_path}")

# 9. FIRM-WISE AGGREGATION


firm_agg_df = (
    product_df
    .groupby("FIRM", dropna=False)
    .agg(
        total_quantity=("Quantity", "sum"),
        total_sales_value=("Value", "sum"),
        total_cgst=("CGST@9%", "sum"),
        total_sgst=("SGST@9%", "sum"),
        distinct_products=("FIRM_PRODUCT", "nunique"),
        line_items=("FIRM_PRODUCT", "count")
    )
    .reset_index()
)

print("\nFIRM-WISE AGGREGATED DATA:")
print(firm_agg_df.head(20).to_string(index=False))
print("\nFirm-level shape:", firm_agg_df.shape)

firm_output_path = r"C:\Users\akank\OneDrive\Desktop\AverxaAI\SAS-Chatbot\Team Updates\Akanksha\firm_wise_sales_summary.xlsx"

firm_agg_df.to_excel(firm_output_path, index=False)

print(f"\nSaved firm-wise summary to:\n{firm_output_path}")


# 10. PRODUCT-WISE AGGREGATION


product_agg_df = (
    product_df
    .groupby("FIRM_PRODUCT", dropna=False)
    .agg(
        total_quantity=("Quantity", "sum"),
        total_sales_value=("Value", "sum"),
        total_cgst=("CGST@9%", "sum"),
        total_sgst=("SGST@9%", "sum"),
        distinct_firms=("FIRM", "nunique"),
        line_items=("FIRM", "count")
    )
    .reset_index()
    .sort_values("total_sales_value", ascending=False)
)

print("\nPRODUCT-WISE AGGREGATED DATA:")
print(product_agg_df.head(20).to_string(index=False))
print("\nProduct-level shape:", product_agg_df.shape)
product_summary_path = r"C:\Users\akank\OneDrive\Desktop\AverxaAI\SAS-Chatbot\Team Updates\Akanksha\product_wise_sales_summary.xlsx"

product_agg_df.to_excel(product_summary_path, index=False)

print(f"\nSaved product-wise summary to:\n{product_summary_path}")
