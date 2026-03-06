import pytest
from src.tools.sql_query_tool import validate_read_only_sql


def test_validate_select_query_passes():
    validate_read_only_sql("SELECT id, email FROM users WHERE created_at >= '2026-01-01'")


def test_validate_non_select_fails():
    with pytest.raises(ValueError):
        validate_read_only_sql("DELETE FROM users")


def test_validate_multi_statement_fails():
    with pytest.raises(ValueError):
        validate_read_only_sql("SELECT * FROM users; SELECT * FROM orders")