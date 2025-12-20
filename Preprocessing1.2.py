import pandas as pd
import numpy as np

df = pd.read_excel("DECEMBER SALE.xls", header=None)
df.replace(r'^\s*$', np.nan, regex=True, inplace=True)

# Remove top 8 unnecessary rows
df = df.iloc[8:].reset_index(drop=True)
df.columns = df.iloc[0]
df = df.iloc[1:].reset_index(drop=True)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["FIRM"] = np.where(
    df["Date"].notna(),
    df["Particulars"],
    np.nan
)
df["FIRM"] = df["FIRM"].ffill()
df["FIRM_PRODUCT"] = np.where(
    df["Date"].notna(),
    np.nan,
    df["Particulars"]
)
df = df.drop(columns=["Particulars"])

df[["Date", "FIRM", "FIRM_PRODUCT"]].head(20)
print("\nCOLUMNS AFTER TRANSFORMATION:")
print(df.columns.tolist())

print("\nSAMPLE DATA (Date, FIRM, FIRM_PRODUCT):")
print(df[["Date", "FIRM", "FIRM_PRODUCT"]].head(20).to_string(index=False))

print("\nFULL DATA (first 20 rows, all columns):")

print(df.head(20).to_string(index=False))

import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
print(df.head(20))
print(df.columns.tolist())
print(df.head(20).to_string(index=False))
