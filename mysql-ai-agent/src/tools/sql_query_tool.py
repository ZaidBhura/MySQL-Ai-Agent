import re
from typing import Any
import pandas as pd

try:
    from src.db.connection import get_db_connection
except ModuleNotFoundError:
    from db.connection import get_db_connection

_DISALLOWED_SQL_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|REPLACE|GRANT|REVOKE|SET)\b",
    re.IGNORECASE,
)


def validate_read_only_sql(sql_query: str) -> None:
    normalized = sql_query.strip().strip(";")
    if not normalized.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    if ";" in normalized:
        raise ValueError("Multiple SQL statements are not allowed.")

    if _DISALLOWED_SQL_PATTERN.search(normalized):
        raise ValueError("Potentially unsafe SQL keyword detected.")


def execute_query(sql_query: str, max_rows: int = 10000) -> pd.DataFrame:
    """Execute a SQL query and return the results as a pandas DataFrame."""
    validate_read_only_sql(sql_query)
    connection = get_db_connection()
    try:
        # Add LIMIT to prevent massive result sets
        limited_query = sql_query.strip().rstrip(';')
        if 'LIMIT' not in limited_query.upper():
            limited_query += f' LIMIT {max_rows}'
        df = pd.read_sql(limited_query, connection)
        return df
    finally:
        connection.close()

def format_query_response(df: pd.DataFrame, sql_query: str) -> dict[str, Any]:
    """Format the query response to include the SQL query and results."""
    return {
        "sql_query": sql_query,
        "row_count": len(df),
        "columns": df.columns.tolist(),
        "results": df.to_dict(orient='records')
    }