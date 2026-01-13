import re

def clean_sql(sql: str) -> str:
    # Remove ```sql ... ```
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    return sql.strip()
