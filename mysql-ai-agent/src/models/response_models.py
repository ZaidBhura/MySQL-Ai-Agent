from pydantic import BaseModel
from typing import List, Any

class SQLGenerationResponse(BaseModel):
    sql_query: str
    tables_used: List[str]
    reasoning: str


class QueryResponse(BaseModel):
    query: str
    sql_query: str
    selected_tables: List[str]
    selected_columns: dict[str, List[str]]
    columns: List[str]
    row_count: int
    results: List[dict[str, Any]]
    message: str = "Query executed successfully"
    success: bool = True