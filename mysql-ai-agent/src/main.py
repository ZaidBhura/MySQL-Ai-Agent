from dotenv import load_dotenv

try:
    from src.agents.sql_agent import SQLAgent
except ModuleNotFoundError:
    from agents.sql_agent import SQLAgent

load_dotenv()

def main():
    print("Welcome to the MySQL AI Agent")
    agent = SQLAgent()
    agent.run_interactive()

if __name__ == "__main__":
    main()