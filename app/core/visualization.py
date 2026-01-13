# app/core/visualization.py

from typing import Dict, List


def select_visualization(data: List[Dict]) -> Dict:
    """
    Decide visualization type based on result shape.
    This function is deterministic (NO LLM).
    """

    if not data:
        return {
            "type": "empty",
            "reason": "No data returned"
        }

    columns = list(data[0].keys())
    row_count = len(data)

    # KPI (single value)
    if row_count == 1 and len(columns) == 1:
        return {
            "type": "kpi",
            "x": None,
            "y": columns[0]
        }

    # KPI with label (e.g. customer + revenue)
    if row_count == 1 and len(columns) == 2:
        return {
            "type": "kpi",
            "label": columns[0],
            "value": columns[1]
        }

    # Category vs metric → bar chart
    if len(columns) == 2 and row_count <= 20:
        return {
            "type": "bar",
            "x": columns[0],
            "y": columns[1]
        }

    # Time series
    if "date" in columns or "voucher_date" in columns:
        return {
            "type": "line",
            "x": "voucher_date" if "voucher_date" in columns else "date",
            "y": columns[-1]
        }

    # Fallback
    return {
        "type": "table",
        "columns": columns
    }
