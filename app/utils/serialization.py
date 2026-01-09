from decimal import Decimal

def normalize_value(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def normalize_row(row: dict) -> dict:
    return {k: normalize_value(v) for k, v in row.items()}


def normalize_data(rows: list[dict]) -> list[dict]:
    return [normalize_row(row) for row in rows]
