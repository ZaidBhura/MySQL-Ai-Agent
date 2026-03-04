from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from landchain_core.output_parsers import PydanticOutputParser
import pymysql
import pandas as pd
import os


load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# setup LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Database connection setup
def get_db_connection():
    """Create a database connection using credentials from .env"""
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )
    return connection

def query_database(sql_query: str) -> pd.DataFrame:
    """Execute a SQL query and return results as a pandas DataFrame"""
    connection = get_db_connection()
    try:
        df = pd.read_sql(sql_query, connection)
        return df
    finally:
        connection.close()

# Example: Query database and pass to AI agent
# df = query_database("SELECT * FROM your_table LIMIT 5")
# response = llm.invoke(f"Analyze this data: {df.to_string()}")
# print(response) 

#prompt template
