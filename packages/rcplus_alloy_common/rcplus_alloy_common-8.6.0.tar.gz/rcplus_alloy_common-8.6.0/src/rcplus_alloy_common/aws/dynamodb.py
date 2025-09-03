import warnings
from datetime import datetime
from typing import Any, Literal, TypedDict

import boto3
import pandas as pd

from .utils import datetime_to_str
from .wr import get_database, to_parquet, dynamodb_read_items


class AttributeUpdatesItem(TypedDict):
    Action: Literal["ADD", "PUT", "DELETE"]
    Value: Any


class DynamoDBAthenaSynchronizer:
    def __init__(
        self,
        table_name,
        s3_bucket,
        athena_table_name,
        columns: list[str] | None = None,
        dtypes: dict[str, str] | None = None,
        index_col: str | None = None,
        filter_expression: str | None = None,
        expression_attribute_values: dict[str, Any] | None = None,
        pyarrow_additional_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.table_name = table_name
        self.athena_table_name = athena_table_name
        self.athena_database_name = get_database()
        self.athena_s3_path = f"s3://{s3_bucket}/{self.athena_database_name}/{self.athena_table_name}"
        self.columns = columns
        self.dtypes = dtypes
        self.index_col = index_col
        self.filter_expression = filter_expression
        self.expression_attribute_values = expression_attribute_values
        self.pyarrow_additional_kwargs = pyarrow_additional_kwargs
        self.table_snapshot = self.sync_table()

    @staticmethod
    def _parse_dates(df: pd.DataFrame, dtypes: dict | None = None) -> pd.DataFrame:
        """
        Parses the dates in the dataframe.
        """
        for col in df.columns:
            if dtypes and col in dtypes:
                if not pd.api.types.is_datetime64_any_dtype(pd.Series(dtype=dtypes[col])):
                    continue
            if isinstance(df[col].dtype, pd.StringDtype) or df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col], errors="raise", utc=True, format="ISO8601")
                except ValueError:
                    pass
        return df

    def sync_table(
        self,
    ) -> pd.DataFrame:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # ignore warnings for scan operations
            table = dynamodb_read_items(
                table_name=self.table_name,
                allow_full_scan=True,
                filter_expression=self.filter_expression,
                expression_attribute_values=self.expression_attribute_values,
                pyarrow_additional_kwargs=self.pyarrow_additional_kwargs,
            )
        table = self._parse_dates(table, self.dtypes)

        if self.columns:
            for col in self.columns:
                if col not in table.columns:
                    table[col] = None

        if self.dtypes:
            for col, dtype in self.dtypes.items():
                table[col] = table[col].astype(dtype)  # type: ignore[call-overload]

        if self.index_col:
            table.set_index(self.index_col, inplace=True, drop=False)

        to_parquet(
            table,
            dataset=True,
            database=self.athena_database_name,
            path=self.athena_s3_path,
            mode="overwrite",
            table=self.athena_table_name,
        )
        return table

    def update(
        self,
        items: list[tuple[dict[str, Any], dict[str, AttributeUpdatesItem]]],
        sync_athena: bool = False,
    ):
        table = boto3.resource("dynamodb").Table(self.table_name)
        for key, attribute_updates in items:
            for k, v in attribute_updates.items():
                if isinstance(v["Value"], (pd.Timestamp, datetime)):
                    attribute_updates[k]["Value"] = datetime_to_str(v["Value"], format="dynamodb")
            table.update_item(
                Key=key,
                AttributeUpdates=attribute_updates,
            )

        if sync_athena:
            self.table_snapshot = self.sync_table()
