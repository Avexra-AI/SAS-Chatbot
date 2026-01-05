import re
from lxml import etree
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_XML = BASE_DIR / "daybook_raw.xml"
CLEAN_XML = BASE_DIR / "daybook_clean.xml"

def clean_tally_xml(input_path, output_path):
    with open(input_path, "rb") as f:
        raw = f.read()

    cleaned = re.sub(
        b'[\x00-\x08\x0B\x0C\x0E-\x1F]',
        b'',
        raw
    )

    text = cleaned.decode("utf-8", errors="ignore")
    text = re.sub(r'&#x?[0-9A-Fa-f]+;', '', text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ XML fully cleaned")

# ---------- PIPELINE ----------
clean_tally_xml(RAW_XML, CLEAN_XML)

tree = etree.parse(str(CLEAN_XML))
root = tree.getroot()

vouchers = root.findall(".//VOUCHER")
print("Total vouchers:", len(vouchers))

data = []
for v in vouchers:
    data.append({
        "voucher_no": v.findtext("VOUCHERNUMBER"),
        "date": v.findtext("DATE"),
        "voucher_type": v.findtext("VOUCHERTYPENAME"),
        "narration": v.findtext("NARRATION"),
    })

df = pd.DataFrame(data)
print(df.head())
