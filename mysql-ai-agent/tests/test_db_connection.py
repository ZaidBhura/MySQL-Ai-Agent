import pytest
import pymysql
import os
from src.db.connection import get_db_connection

def test_get_db_connection():
    required_keys = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    if any(not os.getenv(key) for key in required_keys):
        pytest.skip("Database credentials are not configured in environment.")

    try:
        connection = get_db_connection()
    except pymysql.err.OperationalError:
        pytest.skip("MySQL server is not reachable in this environment.")

    assert connection is not None
    assert isinstance(connection, pymysql.connections.Connection)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        database = cursor.fetchone()
        assert database is not None

    connection.close()