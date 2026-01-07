import sqlite3

conn = sqlite3.connect("local_store/tally_live.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS vouchers (
    voucher_no TEXT,
    date TEXT,
    type TEXT,
    fingerprint TEXT PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS ledger_entries (
    fingerprint TEXT,
    ledger TEXT,
    amount REAL,
    dr_cr TEXT
)
""")

def upsert(voucher):
    cur.execute("""
    INSERT OR IGNORE INTO vouchers
    VALUES (?, ?, ?, ?)
    """, (
        voucher["voucher_no"],
        voucher["date"],
        voucher["type"],
        voucher["fingerprint"]
    ))

    for e in voucher["entries"]:
        cur.execute("""
        INSERT INTO ledger_entries
        VALUES (?, ?, ?, ?)
        """, (
            voucher["fingerprint"],
            e["ledger"],
            e["amount"],
            e["dr_cr"]
        ))

    conn.commit()

