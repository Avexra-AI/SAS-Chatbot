import pandas as pd
import os

# FULL ABSOLUTE PATH (NO GUESSING)
file_path = r"C:\Users\akank\OneDrive\Desktop\AverxaAI\SAS-Chatbot\Team Updates\Akanksha\DECEMBER SALE.xls"

# SAFETY CHECK (this is what serious engineers do)
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found at: {file_path}")

# READ EXCEL AND SKIP TOP 8 ROWS
df = pd.read_excel(file_path, skiprows=8)

# CLEAN COLUMN NAMES
df.columns = df.columns.str.strip()

# VERIFY
print("Columns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nShape:", df.shape)


#2. removing coulumns
cols_to_drop = [
    "SALES @18% Inter-State",
    "IGST @18%",
    "Freight"
]

df = df.drop(columns=cols_to_drop, errors="ignore")
print("Remaining columns:")
print(df.columns.tolist())
print("Columns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nShape:", df.shape)

# 3. adding frim name and frim product in place of particulars
df["is_firm_row"] = df["Date"].notna()
df["FIRM"] = df["Particulars"].where(df["is_firm_row"])
df["FIRM"] = df["FIRM"].ffill()
df["FIRM_PRODUCT"] = df["Particulars"].where(~df["is_firm_row"])
df = df.drop(columns=["Particulars"])

# 4. REORDER COLUMNS (Date → Firm → Product → Voucher → rest)
# REORDER COLUMNS: Date → Firm → Product → Voucher → rest
priority_cols = [
    "Date",
    "FIRM",
    "FIRM_PRODUCT",
    "Voucher Type",
    "Voucher No."
]

df = df[
    priority_cols +
    [col for col in df.columns if col not in priority_cols]
]

print("\nFINAL DATA (ORDERED COLUMNS):")
print(df.head(20).to_string(index=False))
print("\nFinal Shape:", df.shape)








#4. here created new file to see result from the changes
output_path = "cleaned_sales_dataset.xlsx"
df.to_excel(output_path, index=False)
print(f"Saved cleaned dataset to: {output_path}")
