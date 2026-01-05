import re
from lxml import etree
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).resolve().parent
RAW_XML = BASE_DIR / "daybook_raw.xml"
CLEAN_XML = BASE_DIR / "daybook_clean.xml"
DB_PATH = BASE_DIR / "tally.db"

# ---------------- 1. SANITIZE XML ----------------
def sanitize_tally_xml(input_path, output_path):
    with open(input_path, "rb") as f:
        raw = f.read()

    # remove illegal control chars
    cleaned = re.sub(
        b'[\x00-\x08\x0B\x0C\x0E-\x1F]',
        b'',
        raw
    )

    text = cleaned.decode("utf-8", errors="ignore")

    # remove invalid numeric char refs (&#4;, &#x04;)
    text = re.sub(r'&#x?[0-9A-Fa-f]+;', '', text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ XML sanitized")

sanitize_tally_xml(RAW_XML, CLEAN_XML)

# ---------------- 2. PARSE XML ----------------
tree = etree.parse(str(CLEAN_XML))
root = tree.getroot()
vouchers = root.findall(".//VOUCHER")
print(f"✅ Vouchers found: {len(vouchers)}")

# ---------------- 3. EXTRACT DATA ----------------
voucher_rows = []
ledger_rows = []

for v in vouchers:
    voucher_no = v.findtext("VOUCHERNUMBER")
    date = v.findtext("DATE")
    vtype = v.findtext("VOUCHERTYPENAME")
    narration = v.findtext("NARRATION")

    voucher_rows.append({
        "voucher_no": voucher_no,
        "voucher_date": date,
        "voucher_type": vtype,
        "narration": narration
    })

    entries = v.findall(".//ALLLEDGERENTRIES.LIST")
    for e in entries:
        ledger = e.findtext("LEDGERNAME")
        amount = e.findtext("AMOUNT")

        if amount is None:
            continue

        amount = float(amount)
        dr_cr = "DR" if amount > 0 else "CR"

        ledger_rows.append({
            "voucher_no": voucher_no,
            "ledger_name": ledger,
            "amount": abs(amount),
            "dr_cr": dr_cr
        })

df_vouchers = pd.DataFrame(voucher_rows)
df_ledgers = pd.DataFrame(ledger_rows)

print("✅ Ledger entries:", len(df_ledgers))

# ---------------- 4. STORE IN SQLITE ----------------
engine = create_engine(f"sqlite:///{DB_PATH}")

df_vouchers.to_sql("vouchers", engine, if_exists="replace", index=False)
df_ledgers.to_sql("ledger_entries", engine, if_exists="replace", index=False)

print("✅ Data stored in tally.db")

# ---------------- DONE ----------------
print("🎯 PIPELINE COMPLETE")
