import psycopg2

from app.config import DATABASE_URL


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def insert_raw_payload(ingestion_id, company_id, entity_type, payload):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO raw_tally_ingestion
        (ingestion_id, company_id, entity_type, fetched_at, payload, source)
        VALUES (%s, %s, %s, now(), %s, %s)
        """,
        (ingestion_id, company_id, entity_type, payload, "tally")
    )

    conn.commit()
    cur.close()
    conn.close()


def insert_audit_log(upload_id, message):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO upload_audit_logs
        (audit_id, upload_id, message)
        VALUES (gen_random_uuid(), %s, %s)
        """,
        (upload_id, message)
    )

    conn.commit()
    cur.close()
    conn.close()


def insert_staged_voucher(upload_id, voucher):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO staged_vouchers
        (id, upload_id, voucher_no, voucher_date, amount)
        VALUES (gen_random_uuid(), %s, %s, %s, %s)
        """,
        (
            upload_id,
            voucher["voucher_no"],
            voucher["voucher_date"],
            voucher["amount"]
        )
    )

    conn.commit()
    cur.close()
    conn.close()
