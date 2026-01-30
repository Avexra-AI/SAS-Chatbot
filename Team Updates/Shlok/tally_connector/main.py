from config import CONNECTOR_NAME, CONNECTOR_VERSION, SOURCE
from tally_client import send_request
from parser import xml_to_json
from db import insert_raw_payload
from datetime import datetime, timezone
import json
import uuid


# -----------------------------
# XML REQUEST BUILDERS
# -----------------------------

def ledger_request_xml():
    return """
    <ENVELOPE>
      <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
      </HEADER>
      <BODY>
        <EXPORTDATA>
          <REQUESTDESC>
            <REPORTNAME>List of Accounts</REPORTNAME>
            <STATICVARIABLES>
              <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """


def voucher_request_xml():
    return """
    <ENVELOPE>
      <HEADER>
        <TALLYREQUEST>Export Data</TALLYREQUEST>
      </HEADER>
      <BODY>
        <EXPORTDATA>
          <REQUESTDESC>
            <REPORTNAME>Voucher Register</REPORTNAME>
            <STATICVARIABLES>
              <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """


# -----------------------------
# CONFIG
# -----------------------------

COMPANY_ID = str(uuid.uuid4())  # temp, will map later


# -----------------------------
# ENVELOPE BUILDER
# -----------------------------

def build_envelope(entity_type, request_type, raw_payload):
    return {
        "connector": {
            "name": CONNECTOR_NAME,
            "version": CONNECTOR_VERSION,
            "source": SOURCE
        },
        "company_id": COMPANY_ID,
        "entity_type": entity_type,
        "request_type": request_type,
        "fetched_at": datetime.utcnow().isoformat(),
        "raw_payload": raw_payload
    }


# -----------------------------
# FETCH + STORE
# -----------------------------

def fetch_and_store(entity_type, request_type, xml_request):
    xml_response = send_request(xml_request)
    parsed_json = xml_to_json(xml_response)

    envelope = build_envelope(
        entity_type=entity_type,
        request_type=request_type,
        raw_payload=parsed_json
    )

    insert_raw_payload(
        company_id=COMPANY_ID,
        entity_type=entity_type,
        payload=json.dumps(envelope)
    )

    print(f"✅ Stored {entity_type} data successfully")


# -----------------------------
# ENTRY POINT
# -----------------------------

if __name__ == "__main__":

    # Fetch Ledgers
    fetch_and_store(
        entity_type="ledger",
        request_type="list_of_accounts",
        xml_request=ledger_request_xml()
    )

    # Fetch Vouchers
    fetch_and_store(
        entity_type="voucher",
        request_type="voucher_register",
        xml_request=voucher_request_xml()
    )
