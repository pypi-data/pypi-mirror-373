import yaml


def read_table_from_yaml_schema(file_path, table_name) -> dict:
    """Reads the YAML schema file and returns tables configuration."""
    with open(file_path, "r") as file:
        schema = yaml.safe_load(file)
        # Assume unique table names within a schema file
        for source in schema["sources"]:
            for table in source["tables"]:
                if table["name"] == table_name:
                    return table

    raise KeyError(f"{table_name} not found from {file_path}")


def get_partition_columns_with_type(schema: dict) -> dict:
    """Returns dict of partition columns with their types."""
    return {
        col["name"]: col["type"] for col in schema.get("external", {}).get("partitions", [])
    }


def get_partition_columns_list(schema: dict) -> list[str]:
    """Returns list of partition columns."""
    return list(get_partition_columns_with_type(schema))


def get_columns_with_types(schema: dict, include_partition: bool = True) -> dict:
    """
    Returns dict of columns with their types.
    include_partitions defines whether partitioned columns are included or not.
    """
    partition_columns = get_partition_columns_with_type(schema) if include_partition else {}
    return {
        col["name"]: col["type"]
        for col in schema["columns"]
    } | partition_columns


def normalize_column_description(description: str) -> str:
    """Must not contain newlines and shall be < 256 characters."""
    return description.replace("\n", " ")[:255]


def get_columns_with_comments(schema: dict) -> dict:
    """Returns dict of all columns with their comments"""
    partition_columns = {
        col["name"]: normalize_column_description(col["description"])
        for col in schema.get("external", {}).get("partitions", [])
    }
    return {
        col["name"]: normalize_column_description(col["description"])
        for col in schema["columns"]
    } | partition_columns


def get_sql_columns_with_comments(schema: dict) -> str:
    """Returns string of all columns with type and comments"""
    columns = []
    for col in schema["columns"]:
        name = str(col["name"]).strip()
        col_type = str(col["type"]).strip()
        description = normalize_column_description(str(col["description"]))
        if " " in name or "'" in description:
            raise ValueError("Spaces in column names and ' in description not allowed")

        columns.append({"name": name, "type": col_type, "description": description})

    for col in schema.get("external", {}).get("partitions", []):
        name = str(col["name"]).strip()
        col_type = str(col["type"]).strip()
        description = normalize_column_description(str(col["description"]))
        if " " in name or "'" in description:
            raise ValueError("Spaces in column names and ' in description not allowed")

        columns.append({"name": name, "type": col_type, "description": description})

    result = (
        ", ".join(
            [
                f"{col['name']} {col['type']} COMMENT '{col['description']}'"
                for col in columns
            ]
        )
    )
    return result
