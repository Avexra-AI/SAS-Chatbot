import xml.etree.ElementTree as ET


def parse_tally_vouchers(xml_string: str):
    root = ET.fromstring(xml_string)
    vouchers = []

    for v in root.findall(".//VOUCHER"):
        vouchers.append({
            "voucher_no": v.findtext("VOUCHERNUMBER"),
            "voucher_date": v.findtext("DATE"),
            "amount": v.findtext("AMOUNT"),
        })

    return vouchers
