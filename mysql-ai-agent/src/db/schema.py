from typing import Any

from pydantic import BaseModel

try:
    from src.db.connection import get_db_connection
except ModuleNotFoundError:
    from db.connection import get_db_connection


class Column(BaseModel):
    table_name: str
    name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool = False


class TableSchema(BaseModel):
    table_name: str
    columns: list[Column]


class ForeignKeyRelation(BaseModel):
    table_name: str
    column_name: str
    referenced_table_name: str
    referenced_column_name: str


class DatabaseSchema(BaseModel):
    tables: list[TableSchema]
    foreign_keys: list[ForeignKeyRelation]


def get_table_names() -> list[str]:
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    finally:
        connection.close()


def get_columns_for_table(table_name: str) -> list[Column]:
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_KEY
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION;
                """,
                (table_name,),
            )
            rows = cursor.fetchall()
            return [
                Column(
                    table_name=table_name,
                    name=row[0],
                    data_type=row[1],
                    is_nullable=row[2] == "YES",
                    is_primary_key=row[3] == "PRI",
                )
                for row in rows
            ]
    finally:
        connection.close()


def get_foreign_key_relations() -> list[ForeignKeyRelation]:
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    TABLE_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND REFERENCED_TABLE_NAME IS NOT NULL;
                """
            )
            rows = cursor.fetchall()
            return [
                ForeignKeyRelation(
                    table_name=row[0],
                    column_name=row[1],
                    referenced_table_name=row[2],
                    referenced_column_name=row[3],
                )
                for row in rows
            ]
    finally:
        connection.close()


def get_schema() -> DatabaseSchema:
    tables = get_table_names()
    table_schemas = [
        TableSchema(table_name=table_name, columns=get_columns_for_table(table_name))
        for table_name in tables
    ]
    return DatabaseSchema(tables=table_schemas, foreign_keys=get_foreign_key_relations())


def schema_to_prompt_text(schema: DatabaseSchema) -> str:
    lines: list[str] = []
    for table in schema.tables:
        col_text = ", ".join(
            [
                f"{column.name} ({column.data_type}{' PK' if column.is_primary_key else ''})"
                for column in table.columns
            ]
        )
        lines.append(f"- {table.table_name}: {col_text}")

    if schema.foreign_keys:
        lines.append("Foreign keys:")
        for fk in schema.foreign_keys:
            lines.append(
                f"- {fk.table_name}.{fk.column_name} -> "
                f"{fk.referenced_table_name}.{fk.referenced_column_name}"
            )
    return "\n".join(lines)


def get_columns_map(schema: DatabaseSchema) -> dict[str, list[str]]:
    return {
        table.table_name: [column.name for column in table.columns]
        for table in schema.tables
    }


def get_foreign_key_dict(schema: DatabaseSchema) -> list[dict[str, Any]]:
    return [fk.model_dump() for fk in schema.foreign_keys]