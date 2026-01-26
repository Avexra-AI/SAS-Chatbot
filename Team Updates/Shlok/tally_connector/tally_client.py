import requests
from config import TALLY_URL

HEADERS = {
    "Content-Type": "application/xml"
}

def send_request(xml_body: str) -> str:
    response = requests.post(
        TALLY_URL,
        data=xml_body.encode("utf-8"),
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    return response.text
