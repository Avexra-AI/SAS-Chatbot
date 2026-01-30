import os
import uuid
import json
from datetime import datetime, timezone

from app.tally_client import send_request
from app.parser import parse_tally_vouchers
from app.db import (
    insert_raw_payload,
    insert_audit_log,
    insert_staged_voucher
)
from app.config import CONNECTOR_NAME, CONNECTOR_VERSION

RAW_STORAGE_PATH = "storage/raw"
os.makedirs(RAW_STORAGE_PATH, exist_ok=True)


def ingest(entity_type, request_type, xml_request):
    upload_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())

    insert_audit_log(upload_id, "Ingestion started")

    # Fetch XML from Tally / Mock
    xml_response = send_request(xml_request)
    insert_audit_log(upload_id, "XML received")

    # Save raw XML file (IMMUTABLE)
    file_path = f"{RAW_STORAGE_PATH}/{upload_id}.xml"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(xml_response)

    insert_audit_log(upload_id, "Raw XML stored to filesystem")

    # Build envelope
    envelope = {
        "connector": {
            "name": CONNECTOR_NAME,
            "version": CONNECTOR_VERSION
        },
        "company_id": company_id,
        "entity_type": entity_type,
        "request_type": request_type,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_xml_path": file_path
    }

    insert_raw_payload(
        ingestion_id=upload_id,
        company_id=company_id,
        entity_type=entity_type,
        payload=json.dumps(envelope)
    )

    insert_audit_log(upload_id, "Raw payload stored in DB")

    # Parse XML → staging
    vouchers = parse_tally_vouchers(xml_response)
    for v in vouchers:
        insert_staged_voucher(upload_id, v)

    insert_audit_log(upload_id, "Staging tables populated")

    return {
        "status": "success",
        "upload_id": upload_id,
        "entity_type": entity_type
    }
