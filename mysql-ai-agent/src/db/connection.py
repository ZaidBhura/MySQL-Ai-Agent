from dotenv import load_dotenv
import pymysql
import os

load_dotenv()

def get_db_connection():
    """Create a MySQL connection using credentials from environment variables."""
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        autocommit=True,
    )