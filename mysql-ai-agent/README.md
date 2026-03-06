# MySQL AI Agent

This project is an AI-powered MySQL query assistant. You describe what data you want in plain English, then the agent:

1. Discovers your tables/columns.
2. Asks you which tables and exact columns it is allowed to use.
3. Generates a safe read-only SQL query.
4. Executes the query via `pymysql` + `pandas`.
5. Returns both the SQL and the resulting rows.

It supports single-table and multi-table queries (joins), using discovered foreign-key relations.

## Project Structure

```
mysql-ai-agent
├── src
│   ├── main.py                # Entry point of the application
│   ├── db                     # Database-related functionalities
│   │   ├── __init__.py        # Marks the db directory as a package
│   │   ├── connection.py       # Functions for establishing a database connection
│   │   └── schema.py          # Defines the database schema and models
│   ├── agents                  # Contains agent logic
│   │   ├── __init__.py        # Marks the agents directory as a package
│   │   └── sql_agent.py       # Logic for handling SQL queries
│   ├── tools                   # Tools for interacting with the database
│   │   ├── __init__.py        # Marks the tools directory as a package
│   │   ├── sql_query_tool.py   # Tool for executing SQL queries
│   │   ├── table_discovery_tool.py # Tool for discovering available tables
│   │   └── column_prompt_tool.py # Tool for prompting user for column names
│   └── types                   # Type definitions for responses
│   └── models                   # Type definitions for responses
│       └── response_models.py  # Pydantic models for response structures
├── tests                       # Unit tests for the application
│   ├── test_sql_agent.py      # Tests for SQL agent functionality
│   └── test_db_connection.py   # Tests for database connection functionality
├── requirements.txt            # Project dependencies
├── .env.example                # Example environment variables for database connection
└── README.md                   # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mysql-ai-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory based on the `.env.example` file, and fill in your database connection details.

## Environment Variables

Create `.env` from `.env.example` and set:

- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_PORT` (optional, default `3306`)
- `OPENAI_API_KEY`

## Usage

Run:

```bash
python src/main.py
```

Then ask questions such as:

- "Get all customer IDs created between 2025-01-01 and 2025-12-31"
- "Show customer IDs and feedback scores for March, joined with feedback table"

The agent will ask you to confirm table and column names before building SQL.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.