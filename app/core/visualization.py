# app/core/visualization.py

from typing import Dict, List


DATE_COLUMNS = {"date", "voucher_date", "movement_date", "created_at"}


def is_numeric(value):
    return isinstance(value, (int, float))


def select_visualization(data: List[Dict]) -> Dict:
    """
    Deterministic visualization selector.
    NO LLM. NO guessing.
    """

    # --------------------------------------------------
    # 0️⃣ Empty result
    # --------------------------------------------------
    if not data:
        return {
            "type": "empty",
            "reason": "No data returned"
        }

    columns = list(data[0].keys())
    row_count = len(data)

    numeric_cols = []
    categorical_cols = []

    for col in columns:
        sample_val = data[0].get(col)
        if is_numeric(sample_val):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    has_date = any(col in DATE_COLUMNS for col in columns)

    # --------------------------------------------------
    # 1️⃣ KPI (single numeric value)
    # --------------------------------------------------
    if row_count == 1 and len(numeric_cols) == 1:
        return {
            "type": "kpi",
            "value": numeric_cols[0]
        }

    # --------------------------------------------------
    # 2️⃣ KPI with label (e.g. name + value)
    # --------------------------------------------------
    if row_count == 1 and len(columns) == 2 and len(numeric_cols) == 1:
        label_col = categorical_cols[0]
        value_col = numeric_cols[0]
        return {
            "type": "kpi",
            "label": label_col,
            "value": value_col
        }

    # --------------------------------------------------
    # 3️⃣ Line chart (time series)
    # --------------------------------------------------
    if has_date and len(numeric_cols) == 1:
        date_col = next(col for col in columns if col in DATE_COLUMNS)
        return {
            "type": "line",
            "x": date_col,
            "y": numeric_cols[0]
        }

    # --------------------------------------------------
    # 4️⃣ Area chart (time series with volume emphasis)
    # --------------------------------------------------
    if has_date and len(numeric_cols) == 1 and row_count > 10:
        date_col = next(col for col in columns if col in DATE_COLUMNS)
        return {
            "type": "area",
            "x": date_col,
            "y": numeric_cols[0]
        }

    # --------------------------------------------------
    # 5️⃣ Simple Bar chart (category vs metric)
    # --------------------------------------------------
    if len(columns) == 2 and len(numeric_cols) == 1 and row_count <= 20:
        return {
            "type": "bar",
            "x": categorical_cols[0],
            "y": numeric_cols[0]
        }

    # --------------------------------------------------
    # 6️⃣ Grouped / Stacked Bar (2 dimensions + 1 metric)
    # --------------------------------------------------
    if len(columns) == 3 and len(numeric_cols) == 1:
        return {
            "type": "grouped_bar",
            "x": categorical_cols[0],
            "group": categorical_cols[1],
            "y": numeric_cols[0]
        }

    # --------------------------------------------------
    # 7️⃣ Histogram (single numeric distribution)
    # --------------------------------------------------
    if len(columns) == 1 and len(numeric_cols) == 1 and row_count > 20:
        return {
            "type": "histogram",
            "value": numeric_cols[0]
        }

    # --------------------------------------------------
    # 8️⃣ Fallback → Table (SAFE DEFAULT)
    # --------------------------------------------------
    return {
        "type": "table",
        "columns": columns
    }
