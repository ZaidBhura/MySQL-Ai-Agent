def _parse_comma_list(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def prompt_for_tables(available_tables: list[str]) -> list[str]:
    print("\nAvailable tables:")
    for index, table_name in enumerate(available_tables, start=1):
        print(f"  {index}. {table_name}")

    raw_tables = input(
        "\nSelect table names (comma-separated), or type 'all' to allow all tables: "
    ).strip()

    if not raw_tables or raw_tables.lower() == "all":
        return available_tables

    selected = _parse_comma_list(raw_tables)
    validated = [table for table in selected if table in available_tables]
    return validated or available_tables


def prompt_for_columns_by_table(
    selected_tables: list[str], columns_by_table: dict[str, list[str]]
) -> dict[str, list[str]]:
    selection: dict[str, list[str]] = {}

    for table_name in selected_tables:
        available_columns = columns_by_table.get(table_name, [])
        print(f"\nColumns in '{table_name}':")
        print("  " + ", ".join(available_columns))

        raw_columns = input(
            "Choose column names for this table (comma-separated), "
            "or type 'all': "
        ).strip()

        if not raw_columns or raw_columns.lower() == "all":
            selection[table_name] = available_columns
            continue

        requested = _parse_comma_list(raw_columns)
        valid = [column for column in requested if column in available_columns]
        selection[table_name] = valid or available_columns

    return selection