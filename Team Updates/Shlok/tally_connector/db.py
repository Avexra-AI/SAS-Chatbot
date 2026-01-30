import psycopg2
import uuid
from config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def insert_raw_payload(company_id, entity_type, payload):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO raw_tally_ingestion (
        ingestion_id,
        company_id,
        entity_type,
        fetched_at,
        payload,
        source
    )
    VALUES (%s, %s, %s, NOW(), %s, %s)
    """

    cur.execute(
        query,
        (
            str(uuid.uuid4()),
            company_id,
            entity_type,
            payload,
            "tally"
        )
    )

    conn.commit()
    cur.close()
    conn.close()
