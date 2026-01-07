from lxml import etree
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CLEAN_XML = BASE_DIR / "daybook_clean.xml"

tree = etree.parse(str(CLEAN_XML))
root = tree.getroot()

rows = []

for v in root.findall(".//VOUCHER"):
    voucher_no = v.findtext("VOUCHERNUMBER")
    date = v.findtext("DATE")
    voucher_type = v.findtext("VOUCHERTYPENAME")

    # Ledger entries (critical part)
    entries = v.findall(".//ALLLEDGERENTRIES.LIST")

    for e in entries:
        ledger = e.findtext("LEDGERNAME")
        amount = e.findtext("AMOUNT")

        if amount is None:
            continue

        amount = float(amount)

        dr_cr = "DR" if amount > 0 else "CR"

        rows.append({
            "voucher_no": voucher_no,
            "date": date,
            "voucher_type": voucher_type,
            "ledger": ledger,
            "amount": abs(amount),
            "dr_cr": dr_cr
        })

df = pd.DataFrame(rows)
print(df.head())
print("Total ledger rows:", len(df))
