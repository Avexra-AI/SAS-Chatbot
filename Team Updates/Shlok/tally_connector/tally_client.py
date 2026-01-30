import requests
from app.config import TALLY_URL


def send_request(xml_request: str) -> str:
    response = requests.post(
        TALLY_URL,
        data=xml_request.encode("utf-8"),
        headers={"Content-Type": "application/xml"},
        timeout=30
    )
    response.raise_for_status()
    return response.text
