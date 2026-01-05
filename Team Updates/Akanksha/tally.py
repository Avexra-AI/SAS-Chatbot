import requests
import re
from lxml import etree
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
TALLY_URL = "http://localhost:9000"
RAW_XML = "daybook_raw.xml"
CLEAN_XML = "daybook_clean.xml"

# -----------------------------
# STEP 1: FETCH XML FROM TALLY
# -----------------------------
xml_request = """
<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Export Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <EXPORTDATA>
      <REQUESTDESC>
        <REPORTNAME>Day Book</REPORTNAME>
        <STATICVARIABLES>
          <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
        </STATICVARIABLES>
      </REQUESTDESC>
    </EXPORTDATA>
  </BODY>
</ENVELOPE>
"""

response = requests.post(TALLY_URL, data=xml_request)

with open(RAW_XML, "wb") as f:
    f.write(response.content)

print("✅ Raw XML saved")

# -----------------------------
# STEP 2: CLEAN XML (MANDATORY)
# -----------------------------
with open(RAW_XML, "rb") as f:
    raw = f.read()

cleaned = re.sub(
    b'[\x00-\x08\x0B\x0C\x0E-\x1F]',
    b'',
    raw
)

with open(CLEAN_XML, "wb") as f:
    f.write(cleaned)

print("✅ Clean XML saved")

# -----------------------------
# STEP 3: PARSE CLEAN XML
# -----------------------------
tree = etree.parse(CLEAN_XML)
root = tree.getroot()

vouchers = root.findall(".//VOUCHER")
print("Total vouchers:", len(vouchers))

# -----------------------------
# STEP 4: EXTRACT STRUCTURED DATA
# -----------------------------
data = []

for v in vouchers:
    data.append({
        "voucher_no": v.findtext("VOUCHERNUMBER"),
        "date": v.findtext("DATE"),
        "voucher_type": v.findtext("VOUCHERTYPENAME")
    })

df = pd.DataFrame(data)
print(df.head())
