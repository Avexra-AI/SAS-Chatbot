import re

def sanitize(raw):
    cleaned = re.sub(
        b'[\x00-\x08\x0B\x0C\x0E-\x1F]',
        b'',
        raw
    )
    text = cleaned.decode("utf-8", errors="ignore")
    return re.sub(r'&#x?[0-9A-Fa-f]+;', '', text)
