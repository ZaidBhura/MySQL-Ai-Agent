try:
    from src.db.schema import get_columns_for_table, get_table_names
except ModuleNotFoundError:
    from db.schema import get_columns_for_table, get_table_names


def get_available_tables() -> list[str]:
    """Return all table names in the active MySQL database."""
    return get_table_names()


def get_available_columns(table_name: str) -> list[str]:
    """Return all column names for a table."""
    return [column.name for column in get_columns_for_table(table_name)]