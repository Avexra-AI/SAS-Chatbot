from fastapi import APIRouter
from app.services.ingestion import ingest

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/vouchers")
def ingest_vouchers():
    xml = """
    <ENVELOPE>
      <BODY>
        <DATA>
          <VOUCHER>
            <VOUCHERNUMBER>1</VOUCHERNUMBER>
            <DATE>20260119</DATE>
            <AMOUNT>1000</AMOUNT>
          </VOUCHER>
        </DATA>
      </BODY>
    </ENVELOPE>
    """
    return ingest("voucher", "voucher_register", xml)
