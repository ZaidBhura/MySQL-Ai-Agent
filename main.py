from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import pymysql
import pandas as pd
import os
from langchain.agents import create_tool_calling_agent, AgentExecutor 
from tools import search_tool, wiki_tool, save_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]



# setup LLM
llm = ChatOpenAI(model="gpt-4o-mini")

parser = PydanticOutputParser(pydantic_object=ResearchResponse)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         """You are a research assistant that will help generate a research paper. 
         Answer the user query and use neccessary tools.messages=Wrap the output in this format and provide no other text\n{format_instructions}
         """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can i help you research? ")
raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)


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
