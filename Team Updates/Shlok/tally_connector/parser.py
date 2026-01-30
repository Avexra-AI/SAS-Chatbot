import xmltodict
import json

def xml_to_json(xml_response: str) -> dict:
    parsed = xmltodict.parse(xml_response)
    return json.loads(json.dumps(parsed))  # ensure pure JSON
