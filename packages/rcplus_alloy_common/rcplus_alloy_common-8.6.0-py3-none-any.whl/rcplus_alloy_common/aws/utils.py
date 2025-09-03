import logging
from datetime import datetime, timezone

import pandas as pd

from rcplus_alloy_common.aws.wr import read_sql_query

logger = logging.getLogger(__name__)


def str_to_datetime(p_timestamp: str, format: str = "athena") -> datetime:
    """
    In Athena we store the timestamps as not timezone aware. But it is assumed that the timestamps are in UTC.
    In DynamoDB we store the timestamps as timezone aware (but we support to read from timezone unaware timestamps too)
    In Python we should always work with timezone aware timestamps.

    NOTE: in Python 3.11 we could just use datetime.fromisoformat(), since the support for blank separator is added.
    """
    if format == "dynamodb":
        dt_obj = datetime.fromisoformat(p_timestamp)
        if dt_obj.tzinfo is None:
            return dt_obj.replace(tzinfo=timezone.utc)
        return dt_obj.astimezone(timezone.utc)

    if format == "athena":
        return datetime.strptime(p_timestamp, "%Y-%m-%d %H:%M:%S.0").replace(tzinfo=timezone.utc)

    return datetime.strptime(p_timestamp, format)


def datetime_to_str(dt_obj: datetime | pd.Timestamp, format="athena") -> str:
    if format == "athena":
        format = "%Y-%m-%d %H:%M:%S.0"
        return dt_obj.strftime(format)

    if format == "dynamodb":
        if isinstance(dt_obj, pd.Timestamp):
            if dt_obj.tzinfo is None:
                return dt_obj.tz_localize("UTC").isoformat()
            return dt_obj.tz_convert("UTC").isoformat()
        return dt_obj.astimezone(timezone.utc).isoformat()

    return dt_obj.strftime(format)


def _read_sql_p_timestamp(sql):
    logger.debug(f"Execute query:\n{sql}")
    df = read_sql_query(sql, ctas_approach=False)
    p_timestamp = df["p"]
    if p_timestamp.isnull().values[0]:
        return None
    return datetime_to_str(p_timestamp.iloc[0], format="athena")


def get_last_p_timestamp_iceberg(table, database=None, partitioned=False):
    """Get the last p_timestamp from an iceberg table. Partitioned = True if partitioned by p_timestamp"""
    if partitioned:
        column = "coalesce(MAX(partition.p_timestamp), CURRENT_DATE - INTERVAL '1' DAY)"
    else:
        column = "coalesce(MAX(data.p_timestamp.max), CURRENT_DATE - INTERVAL '1' DAY)"

    if database:
        table_name = f'"{database}"."{table}$partitions"'
    else:
        table_name = f'"{table}$partitions"'

    sql = f"""
    SELECT {column} AS p FROM {table_name}
    """
    p_timestamp = _read_sql_p_timestamp(sql)
    return p_timestamp


def get_last_p_timestamp_hive(table, database=None):
    """Get the last p_timestamp from an HIVE table."""
    if database:
        table_name = f'"{database}"."{table}$partitions"'
    else:
        table_name = f'"{table}$partitions"'

    sql = f"""
    SELECT coalesce(MAX(p_timestamp), CURRENT_DATE - INTERVAL '1' DAY) AS p FROM {table_name}
    """
    p_timestamp = _read_sql_p_timestamp(sql)
    return p_timestamp
