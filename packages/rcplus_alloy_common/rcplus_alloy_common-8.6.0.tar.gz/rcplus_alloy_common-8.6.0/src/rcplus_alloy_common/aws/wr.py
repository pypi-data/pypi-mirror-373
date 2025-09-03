import os
from typing import Literal, Iterator, Any, overload
import logging

import pandas as pd
import awswrangler as wr
from awswrangler.athena._utils import _QueryMetadata
from awswrangler.typing import GlueTableSettings, _S3WriteDataReturnValue

from rcplus_alloy_common.aws.wr_utils import (
    get_columns_with_comments,
    get_columns_with_types,
    get_partition_columns_list,
    get_partition_columns_with_type,
    get_sql_columns_with_comments,
    read_table_from_yaml_schema,
)


logger = logging.getLogger(__name__)


def get_database() -> str | None:
    database = os.getenv("TENANT", os.getenv("WR_DATABASE", None))
    return database


def get_s3_output(workgroup=None) -> str | None:
    tenant = os.getenv("TENANT", None)
    if tenant is None:
        return None

    if workgroup is None:
        workgroup = os.getenv("WR_WORKGROUP", "primary")

    workgroup_info = wr.athena.get_work_group(workgroup=workgroup)
    try:
        output_location = workgroup_info["WorkGroup"]["Configuration"]["ResultConfiguration"]["OutputLocation"]
    except KeyError:
        return None

    if workgroup_info["WorkGroup"]["Configuration"]["EnforceWorkGroupConfiguration"]:
        raise ValueError("EnforceWorkGroupConfiguration is set to True, cannot override OutputLocation")
    return f"{output_location}/{tenant}"


@overload
def read_sql_query(
    sql: str,
    database: str | None = ...,
    *,
    chunksize: Literal[None] = ...,
    **kwargs
) -> pd.DataFrame:
    ...


@overload
def read_sql_query(
    sql: str,
    database: str | None = ...,
    *,
    chunksize: int | bool,
    **kwargs
) -> Iterator[pd.DataFrame]:
    ...


def read_sql_query(
    sql: str,
    database: str | None = None,
    *,
    chunksize: int | bool | None = None,
    **kwargs
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    """s3_output is required in order to ensure we separate tenant specific outputs in different locations"""
    database = database if database is not None else get_database()
    if database is None:
        raise ValueError("Database is not set")
    s3_output = kwargs.pop(
        "s3_output",
        get_s3_output(workgroup=kwargs.get("workgroup", None)))
    return wr.athena.read_sql_query(sql, database, s3_output=s3_output, chunksize=chunksize, **kwargs)


@overload
def start_query_execution(
    sql: str,
    *,
    database: str | None = ...,
    s3_output: str | None = ...,
    workgroup: str | None = ...,
    wait: Literal[False] = ...,
    **kwargs,
) -> str:
    ...


@overload
def start_query_execution(
    sql: str,
    *,
    database: str | None = ...,
    s3_output: str | None = ...,
    workgroup: str | None = ...,
    wait: Literal[True],
) -> dict[str, Any]:
    ...


def start_query_execution(
    sql: str,
    *,
    database: str | None = None,
    s3_output: str | None = None,
    workgroup: str | None = None,
    wait: bool = False,
    **kwargs,
) -> str | dict[str, Any]:
    """s3_output is required in order to ensure we separate tenant specific outputs in different locations"""
    database = database if database is not None else get_database()
    s3_output = s3_output if s3_output is not None else get_s3_output(workgroup=workgroup)

    logger.debug(sql)

    return wr.athena.start_query_execution(
        sql=sql,
        database=database,
        s3_output=s3_output,
        workgroup=workgroup or "primary",
        wait=wait,
        **kwargs
    )


@overload
def create_ctas_table(
    sql: str,
    *,
    database: str | None = ...,
    s3_output: str | None = ...,
    workgroup: str | None = ...,
    wait: Literal[False] = ...,
    **kwargs,
) -> dict[str, str]:
    ...


@overload
def create_ctas_table(
    sql: str,
    *,
    database: str | None = ...,
    s3_output: str | None = ...,
    workgroup: str | None = ...,
    wait: Literal[True],
) -> dict[str, _QueryMetadata]:
    ...


def create_ctas_table(
    sql: str,
    *,
    database: str | None = None,
    s3_output: str | None = None,
    workgroup: str | None = None,
    wait: bool = False,
    **kwargs,
) -> dict[str, _QueryMetadata] | dict[str, str]:
    database = database if database is not None else get_database()
    s3_output = s3_output if s3_output is not None else get_s3_output(workgroup=workgroup)
    return wr.athena.create_ctas_table(
        sql,
        database,
        s3_output=s3_output,
        workgroup=workgroup or "primary",
        wait=wait,
        **kwargs
    )  # type: ignore


def get_glue_table_settings(table_schema) -> GlueTableSettings:
    """Creates the settings for the Glue table based on the schema."""
    table_description = table_schema["description"]
    columns_comments = get_columns_with_comments(table_schema)
    return GlueTableSettings(description=table_description, columns_comments=columns_comments)


def validate_path(table: str, database: str, path: str) -> None:
    if not path.startswith("s3://"):
        raise ValueError("path has to start with s3://")

    if database not in path or table not in path:
        raise ValueError("Database and table required in path")


def validate_table_input(
    schema_file_path: str | None,
    columns_types: dict[str, str] | None,
    partitions_types: dict[str, str] | None,
) -> None:

    if (
        (schema_file_path is None and columns_types is None) or
        (schema_file_path is not None and (columns_types is not None or partitions_types is not None))
    ):
        raise ValueError("Supply either only schema_file_path or columns_types/partitions_types")


def to_parquet(
    df: pd.DataFrame,
    path: str,
    table: str | None = None,
    dataset: bool = False,
    database: str | None = None,
    schema_file_path: str | None = None,
    glue_table_settings: GlueTableSettings | None = None,
    dtype: dict[str, str] | None = None,
    partition_cols: list[str] | None = None,
    skip_path_validation: bool = False,
    **kwargs,
) -> _S3WriteDataReturnValue:
    """A wrapper for the awswrangler s3 to_parquet method to read schema."""

    # If dataset is false, to_parquet allows uploading only the df to s3.
    # In that case most of these options are not allowed, and the validation is handled by wr
    if dataset:
        if table is None:
            raise ValueError("Table is not set")

        if schema_file_path and (dtype or partition_cols):
            raise ValueError("Supply either only schema_file_path or dtype and partition_cols")

        database = database if database is not None else get_database()
        if database is None:
            raise ValueError("Database is not set")

        if not skip_path_validation:
            validate_path(table, database, path)

        if schema_file_path is not None:
            table_schema = read_table_from_yaml_schema(schema_file_path, table)
            glue_settings = get_glue_table_settings(table_schema)
            dtype = get_columns_with_types(table_schema)
            partition_cols = get_partition_columns_list(table_schema)
            # Merge the glue table settings
            if glue_table_settings:
                if "description" in glue_settings:
                    glue_table_settings["description"] = glue_settings["description"]
                if "columns_comments" in glue_settings:
                    glue_table_settings["columns_comments"] = glue_settings["columns_comments"]
            else:
                glue_table_settings = glue_settings

    return wr.s3.to_parquet(
        df=df,
        path=path,
        table=table,
        database=database,
        dtype=dtype,
        glue_table_settings=glue_table_settings,
        partition_cols=partition_cols,
        dataset=dataset,
        **kwargs,
    )


def extract_table_creation_params(
    table: str,
    path: str,
    database: str | None,
    columns_types: dict[str, str] | None,
    partitions_types: dict[str, str] | None,
    description: str | None,
    columns_comments: dict[str, str] | None,
    schema_file_path: str | None,
    skip_path_validation: bool,
) -> tuple[str, dict[str, str] | None, dict[str, str] | None, str | None, dict[str, str] | None]:

    database = database if database is not None else get_database()
    if database is None:
        raise ValueError("Database is not set")

    validate_table_input(
        schema_file_path=schema_file_path,
        columns_types=columns_types,
        partitions_types=partitions_types,
    )

    if not skip_path_validation:
        validate_path(table, database, path)

    if schema_file_path is not None:
        table_schema = read_table_from_yaml_schema(schema_file_path, table)
        columns_types = get_columns_with_types(table_schema, include_partition=False)
        partitions_types = get_partition_columns_with_type(table_schema)
        description = table_schema["description"]
        columns_comments = get_columns_with_comments(table_schema)

    return database, columns_types, partitions_types, description, columns_comments


def create_parquet_table(
    table: str,
    path: str,
    database: str | None,
    columns_types: dict[str, str] | None = None,
    partitions_types: dict[str, str] | None = None,
    description: str | None = None,
    columns_comments: dict[str, str] | None = None,
    schema_file_path: str | None = None,
    skip_path_validation: bool = False,
    **kwargs,
) -> None:
    """A wrapper for the awswrangler catalog create_parquet_table method to read schema."""

    database, columns_types, partitions_types, description, columns_comments = extract_table_creation_params(
        table=table,
        path=path,
        database=database,
        columns_types=columns_types,
        partitions_types=partitions_types,
        description=description,
        columns_comments=columns_comments,
        schema_file_path=schema_file_path,
        skip_path_validation=skip_path_validation,
    )

    if columns_types is None:
        raise ValueError("Unexpected error, columns_types is None")

    wr.catalog.create_parquet_table(
        database=database,
        table=table,
        path=path,
        columns_types=columns_types,
        partitions_types=partitions_types,
        description=description,
        columns_comments=columns_comments,
        **kwargs,
    )


def create_json_table(
    table: str,
    path: str,
    database: str | None,
    columns_types: dict[str, str] | None = None,
    partitions_types: dict[str, str] | None = None,
    description: str | None = None,
    columns_comments: dict[str, str] | None = None,
    schema_file_path: str | None = None,
    skip_path_validation: bool = False,
    **kwargs,
) -> None:
    """A wrapper for the awswrangler catalog create_json_table method to read schema."""

    database, columns_types, partitions_types, description, columns_comments = extract_table_creation_params(
        table=table,
        path=path,
        database=database,
        columns_types=columns_types,
        partitions_types=partitions_types,
        description=description,
        columns_comments=columns_comments,
        schema_file_path=schema_file_path,
        skip_path_validation=skip_path_validation,
    )

    if columns_types is None:
        raise ValueError("Unexpected error, columns_types is None")

    wr.catalog.create_json_table(
        database=database,
        table=table,
        path=path,
        columns_types=columns_types,
        partitions_types=partitions_types,
        description=description,
        columns_comments=columns_comments,
        **kwargs,
    )


def create_csv_table(
    table: str,
    path: str,
    database: str,
    columns_types: dict[str, str] | None = None,
    partitions_types: dict[str, str] | None = None,
    description: str | None = None,
    columns_comments: dict[str, str] | None = None,
    schema_file_path: str | None = None,
    skip_path_validation: bool = False,
    **kwargs,
) -> None:
    """A wrapper for the awswrangler catalog create_csv_table method to read schema."""

    database, columns_types, partitions_types, description, columns_comments = extract_table_creation_params(
        table=table,
        path=path,
        database=database,
        columns_types=columns_types,
        partitions_types=partitions_types,
        description=description,
        columns_comments=columns_comments,
        schema_file_path=schema_file_path,
        skip_path_validation=skip_path_validation,
    )

    if columns_types is None:
        raise ValueError("Unexpected error, columns_types is None")

    wr.catalog.create_csv_table(
        database=database,
        table=table,
        path=path,
        columns_types=columns_types,
        partitions_types=partitions_types,
        description=description,
        columns_comments=columns_comments,
        **kwargs,
    )


def create_iceberg_table(  # noqa: PLR0913, PLR0917
    table: str,
    path: str,
    schema_file_path: str | None = None,
    database: str | None = None,
    s3_output: str | None = None,
    workgroup: str | None = None,
    columns_types: dict[str, str] | None = None,
    partitions_types: dict[str, str] | None = None,
    description: str | None = None,
    columns_comments: dict[str, str] | None = None,
    wait: Literal[True, False] = False,
    skip_path_validation: bool = False,
    **kwargs,
) -> str | dict[str, Any]:
    """Helper to create an iceberg table."""
    database = database if database is not None else get_database()
    if database is None:
        raise ValueError("Database is not set")

    validate_table_input(
        schema_file_path=schema_file_path,
        columns_types=columns_types,
        partitions_types=partitions_types,
    )

    if not skip_path_validation:
        validate_path(table, database, path)

    if schema_file_path is not None:
        table_schema = read_table_from_yaml_schema(schema_file_path, table)
        columns_statement = get_sql_columns_with_comments(table_schema)
        partition_columns = ", ".join(get_partition_columns_list(table_schema))
        description = table_schema["description"]
    else:
        columns_types = columns_types or {}
        partitions_types = partitions_types or {}
        columns_comments = columns_comments or {}

        all_columns = columns_types | partitions_types

        columns_arr = []
        for col_name, col_type in all_columns.items():
            col_description = columns_comments.get(col_name, "")
            if " " in col_name or "'" in col_description:
                raise ValueError("Spaces in column names and ' in description not allowed")

            columns_arr.append({"name": col_name, "type": col_type, "description": col_description})

        columns_statement = ", ".join(
            [f"{col['name']} {col['type']} COMMENT '{col['description']}'" for col in columns_arr]
        )

        partition_columns = ", ".join(partitions_types.keys())

    partition_by_statement = f"PARTITIONED BY ({partition_columns})" if partition_columns else ""
    table_comment_statement = f"COMMENT '{description}'" if description else ""

    sql = f"""
    CREATE TABLE IF NOT EXISTS {table} (
            {columns_statement})
        {table_comment_statement}
        {partition_by_statement}
        LOCATION '{path}'
        TBLPROPERTIES (
                'format'='parquet',
                'table_type' ='ICEBERG'
                )
    """

    return start_query_execution(
        sql=sql,
        database=database,
        s3_output=s3_output,
        workgroup=workgroup,
        wait=wait,
        **kwargs,
    )


def dynamodb_read_items(
    table_name: str,
    filter_expression: str | None = None,
    expression_attribute_values: dict[str, Any] | None = None,
    pyarrow_additional_kwargs: dict[str, Any] | None = None,
    **kwargs
) -> pd.DataFrame:
    return wr.dynamodb.read_items(
        table_name=table_name,
        filter_expression=filter_expression,
        expression_attribute_values=expression_attribute_values,
        pyarrow_additional_kwargs=pyarrow_additional_kwargs,
        **kwargs,
    )
