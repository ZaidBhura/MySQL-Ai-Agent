import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

try:
    from src.db.schema import (
        DatabaseSchema,
        get_foreign_key_dict,
        get_schema,
        schema_to_prompt_text,
    )
    from src.tools.sql_query_tool import execute_query, format_query_response
    from src.models.response_models import QueryResponse, SQLGenerationResponse
except ModuleNotFoundError:
    from db.schema import DatabaseSchema, get_foreign_key_dict, get_schema, schema_to_prompt_text
    from tools.sql_query_tool import execute_query, format_query_response
    from models.response_models import QueryResponse, SQLGenerationResponse


class SQLAgent:
    def __init__(self, llm: ChatOpenAI | None = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert MySQL analyst.
Generate exactly one read-only SQL SELECT query.
Rules:
1) Use only selected tables and selected columns provided by user.
2) If multiple tables are needed, join them using the provided foreign keys.
3) Always include clear date filters if user requested date ranges.
4) Return JSON only with keys: sql_query, tables_used, reasoning.
5) No markdown. No comments. No extra keys.
""".strip(),
                ),
                (
                    "human",
                    """
User request:
{question}

Selected tables:
{selected_tables}

Selected columns by table:
{selected_columns}

Schema:
{schema_text}

Foreign keys:
{foreign_keys}
""".strip(),
                ),
            ]
        )

    def _generate_sql(
        self,
        question: str,
        selected_tables: list[str],
        selected_columns: dict[str, list[str]],
        schema: DatabaseSchema,
    ) -> SQLGenerationResponse:
        prompt = self._build_prompt()
        chain = prompt | self.llm
        result = chain.invoke(
            {
                "question": question,
                "selected_tables": json.dumps(selected_tables),
                "selected_columns": json.dumps(selected_columns),
                "schema_text": schema_to_prompt_text(schema),
                "foreign_keys": json.dumps(get_foreign_key_dict(schema)),
            }
        )

        raw = result.content if isinstance(result.content, str) else "".join(result.content)
        parsed = json.loads(raw)
        return SQLGenerationResponse(**parsed)

    def handle_query(
        self,
        question: str,
        selected_tables: list[str],
        selected_columns: dict[str, list[str]],
    ) -> QueryResponse:
        schema = get_schema()
        generation = self._generate_sql(question, selected_tables, selected_columns, schema)
        dataframe = execute_query(generation.sql_query)
        formatted = format_query_response(dataframe, generation.sql_query)

        return QueryResponse(
            query=question,
            sql_query=generation.sql_query,
            selected_tables=selected_tables,
            selected_columns=selected_columns,
            columns=formatted["columns"],
            row_count=formatted["row_count"],
            results=formatted["results"],
            message=generation.reasoning,
            success=True,
        )

    def run_interactive(self) -> None:
        try:
            from src.tools.column_prompt_tool import prompt_for_columns_by_table, prompt_for_tables
            from src.tools.table_discovery_tool import get_available_columns, get_available_tables
        except ModuleNotFoundError:
            from tools.column_prompt_tool import prompt_for_columns_by_table, prompt_for_tables
            from tools.table_discovery_tool import get_available_columns, get_available_tables

        print("MySQL AI Agent ready. Type 'exit' to quit.\n")

        while True:
            question = input("What data do you want? ").strip()
            if not question or question.lower() == "exit":
                break

            tables = get_available_tables()
            if not tables:
                print("No tables found in the current database.")
                continue

            selected_tables = prompt_for_tables(tables)
            columns_by_table = {
                table_name: get_available_columns(table_name)
                for table_name in selected_tables
            }
            selected_columns = prompt_for_columns_by_table(selected_tables, columns_by_table)

            try:
                response = self.handle_query(question, selected_tables, selected_columns)
                print("\nGenerated SQL:")
                print(response.sql_query)
                print("\nRows returned:", response.row_count)
                print("\nData:")
                if response.results:
                    for row in response.results:
                        print(row)
                else:
                    print("No rows matched your filters.")
            except Exception as exc:
                print(f"Error: {exc}")
                print("Please try again with clearer columns, tables, or filters.")