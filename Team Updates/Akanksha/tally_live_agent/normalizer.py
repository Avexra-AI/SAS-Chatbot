from lxml import etree
import hashlib

def voucher_fingerprint(voucher_no, date, vtype, entries):
    base = voucher_no + date + vtype + str(entries)
    return hashlib.sha256(base.encode()).hexdigest()

def normalize(xml_text):
    root = etree.fromstring(xml_text.encode())
    vouchers = []

    for v in root.findall(".//VOUCHER"):
        entries = []

        for e in v.findall(".//ALLLEDGERENTRIES.LIST"):
            amt = e.findtext("AMOUNT")
            if not amt:
                continue

            amt = float(amt)
            entries.append({
                "ledger": e.findtext("LEDGERNAME"),
                "amount": abs(amt),
                "dr_cr": "DR" if amt > 0 else "CR"
            })

        if not entries:
            continue

        voucher_no = v.findtext("VOUCHERNUMBER")
        date = v.findtext("DATE")
        vtype = v.findtext("VOUCHERTYPENAME")

        vouchers.append({
            "voucher_no": voucher_no,
            "date": date,
            "type": vtype,
            "fingerprint": voucher_fingerprint(voucher_no, date, vtype, entries),
            "entries": entries
        })

    return vouchers

