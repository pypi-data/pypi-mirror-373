from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Final

from dateutil.relativedelta import relativedelta

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, Row, SparkSession
    from pyspark.sql.connect.session import SparkSession as SparkRemoteSession
    from pyspark.sql.types import (
        ArrayType,
        DataType,
        StructField,
        StructType,
    )

    AnyType = StructType | ArrayType | StructField | DataType
    Changed = dict[str, str | AnyType | list[str]]

from .....utils import regex_by_group
from ...utils import ENUM_EXTRACT_ARRAY_TYPE

logger = logging.getLogger("jett")
ICEBERG_HIDDEN_PARTITION_FUNC_MAPPING: Final[dict[str, str]] = {
    "years": "year",
    "year": "year",
    "months": "month",
    "month": "month",
    "days": "day",
    "day": "day",
    "date": "day",
    "hours": "hour",
    "hour": "hour",
    "date_hour": "hour",
}
CREATE_TABLE_STMT: Final[
    str
] = """
CREATE EXTERNAL TABLE `{database}`.`{table_name}`(
    {columns}
)
USING ICEBERG
    {partition_by}
TBLPROPERTIES (
    {properties}
)
"""
DEFAULT_TABLE_PROPERTY: Final[dict[str, str]] = {
    "format-version": "2",
    "write.format.default": "parquet",
    "write.distribution-mode": "hash",
    "write.parquet.compression-codec": "zstd",
    "write.avro.compression-codec": "zstd",
    "write.orc.compression-codec": "zstd",
    "write.target-file-size-bytes": "524288000",
    "engine.hive.enabled": "TRUE",
}
SPARK_TEMP_VIEW_NAME: Final[str] = "tool_temp_table"

ListStr = list[str]


def get_iceberg_partition_transform_func(partition_spec: str) -> str:
    """
    extract iceberg's partition transform function
    e.g. days(created_at) -> return as days
    """
    _split: list[str] = partition_spec.split("(", maxsplit=1)
    transform_func: str = ""
    if len(_split) > 1:
        transform_func: str = _split[0]
        if transform_func in ICEBERG_HIDDEN_PARTITION_FUNC_MAPPING:
            transform_func = ICEBERG_HIDDEN_PARTITION_FUNC_MAPPING[
                transform_func
            ]
    return transform_func


def get_table_partition_columns(
    spark: SparkSession | SparkRemoteSession, db_name: str, table_name: str
) -> list[str]:
    """Get partition columns from Iceberg table."""
    partition_spec = []
    rows: list[Row] = spark.sql(
        f"DESC EXTENDED {db_name}.{table_name}"
    ).collect()
    for row in rows:
        if _match := regex_by_group(text=row.col_name, regex=r"Part\s\d+", n=0):
            partition_spec.append(row.data_type)
    return partition_spec


def get_current_snapshot_id(
    spark: SparkSession | SparkRemoteSession, database: str, table_name: str
) -> str:
    """Get the current snapshot id from DDL."""
    rows: list[Row] = spark.sql(
        f"DESC EXTENDED {database}.{table_name}"
    ).collect()
    table_properties: list[str] = [
        row.data_type for row in rows if row.col_name == "Table Properties"
    ]
    # NOTE: Empty table also has table property where value is set to
    #   `current-snapshot-id=none`.
    table_properties: str = table_properties[0]
    snapshot_id: str = regex_by_group(
        text=table_properties, regex=r"current-snapshot-id=(\d+)", n=1
    )
    return snapshot_id


def extract_hidden_partition(partition_spec: list[str]) -> dict[str, str]:
    """Extract Iceberg hidden partitioning spec and function.

    Args:
        partition_spec (list[str]): list of partition specification
            (e.g. ['day(created_at)', 'category'])

    Returns:
        dict: dict of partition specification, the example structure is shown as below
            {
                'created_at': 'years(created_at)'
                'category': 'category',
                'id': 'bucket(4, id)',
                'category': 'truncate(10, category)',
            }
    """
    rs = {}
    for p in partition_spec:
        is_hidden_partition: bool = False
        extracted_col: str = regex_by_group(
            text=p, regex=r"(?<=\()[^)]+(?=\))", n=0
        )  # get everything inside ()

        if extracted_col != "":
            is_hidden_partition = True
            extracted_col = extracted_col.split(",")[-1].strip()

        column: str = extracted_col if is_hidden_partition else p
        rs[column] = p
    return rs


def clean_hidden_partition(partition_spec: str) -> str:
    """Unify iceberg hidden partition transformation supports legacy case like
    days == day.
    """
    _splits: list[str] = partition_spec.replace(" ", "").split("(")
    _key = _splits[0]
    if _key in ICEBERG_HIDDEN_PARTITION_FUNC_MAPPING.keys():
        _val = _splits[1]
        hidden_func = ICEBERG_HIDDEN_PARTITION_FUNC_MAPPING[_key]
        partition_spec = f"{hidden_func}({_val}"
    return partition_spec


def gen_alter_cols(changes: list[Changed]) -> tuple[ListStr, ListStr, ListStr]:
    """Classify and generate the list of columns for add, alter, and drop.

    Returns:
        ListStr: List of new columns, which will be added into table
        ListStr: List of columns, which have type changed
        ListStr: List of columns, which will be dropped from table
    """
    to_add_col_cmds: list[str] = []
    to_alter_col_cmds: list[str] = []
    to_drop_col_cmds: list[str] = []

    for change in changes:
        change_type: str = change.get("type")
        parent_cols: list[str] = change.get("parent_cols")
        add_col_after: str | None = change.get("add_col_after", None)
        source_struct_splits: list[str] = (
            change.get("source_struct_type").simpleString().split(":")
        )
        source_name: str = source_struct_splits[0]
        source_dtype: str = ":".join(source_struct_splits[1:])
        parent_cols_str: str = ".".join(parent_cols)

        if len(parent_cols) != 0:
            source_name: str = f"{parent_cols_str}.{source_name}"

        source_name = source_name.replace(ENUM_EXTRACT_ARRAY_TYPE, "element")

        if change_type == "add_col":
            add_col_cmd = f"{source_name} {source_dtype}"
            if add_col_after:
                add_col_cmd = f"{add_col_cmd} AFTER {add_col_after}"
            else:
                add_col_cmd = f"{add_col_cmd} FIRST"
            to_add_col_cmds.append(add_col_cmd)

        elif change_type == "alter_col":
            to_alter_col_cmds.append(f"{source_name} TYPE {source_dtype}")

        elif change_type == "drop_col":
            to_drop_col_cmds.append(source_name)

    return to_add_col_cmds, to_alter_col_cmds, to_drop_col_cmds


def gen_alter_partitions(
    database: str,
    table_name: str,
    source_partition: dict,
    table_partition: dict,
) -> tuple[list[str], list[str], list[str]]:
    """
    compare what partition specification is needed to drop, replace, or add
    Args:
        database:
        table_name:
        source_partition: a dict, that contains the information of partition specification of configuration
        table_partition: a dict, that contains the information of partition specification of table

    Returns:
        list[str]: List of commands for adding new partitions
        list[str]: List of commands for replacing existing partitions
        list[str]: List of commands for dropping existing partitions
    """

    to_add = []
    to_replace = []
    to_drop = []

    source_keys = source_partition.keys()
    table_keys = table_partition.keys()

    for k, v in source_partition.items():
        if k not in table_keys:  # partition not exist, add new partition
            to_add.append(f"ADD PARTITION FIELD {v}")
        else:
            table_partition_spec = clean_hidden_partition(table_partition[k])
            source_partition_spec = clean_hidden_partition(v)

            if (
                source_partition_spec != table_partition_spec
            ):  # partition spec is diff, replace partition
                to_replace.append(
                    f"REPLACE PARTITION FIELD {table_partition_spec} WITH {v}"
                )

    for k, v in table_partition.items():
        if (
            k not in source_keys
        ):  # partition not exist in configuration, drop existing partition
            to_drop.append(f"DROP PARTITION FIELD {v}")

    to_add = [f"ALTER TABLE {database}.{table_name} {t}" for t in to_add]
    to_replace = [
        f"ALTER TABLE {database}.{table_name} {t}" for t in to_replace
    ]
    to_drop = [f"ALTER TABLE {database}.{table_name} {t}" for t in to_drop]

    return to_add, to_replace, to_drop


def get_boundary_filter_condition(
    transform_func: str, start: datetime, end: datetime
) -> tuple[str, str]:
    """Calculate a new range of start and end based on Iceberg partition
    transform function
    Examples:
        - transform_func is day
        - start is 2024-01-10 12:00:00
        - end is 2024-01-11 17:30:00

        the new range will be 2024-01-10 00:00:00 and 2024-01-12 00:00:00
    """
    mapping = {
        "year": {
            "format": "%Y-01-01 00:00:00",
            "delta": relativedelta(years=1),
        },
        "month": {
            "format": "%Y-%m-01 00:00:00",
            "delta": relativedelta(months=1),
        },
        "day": {
            "format": "%Y-%m-%d 00:00:00",
            "delta": relativedelta(days=1),
        },
        "hour": {
            "format": "%Y-%m-%d %H:00:00",
            "delta": relativedelta(hours=1),
        },
    }
    val = mapping[transform_func]
    min_val_str = (start - val["delta"]).strftime(val["format"])
    max_val_str = (end + val["delta"]).strftime(val["format"])
    return min_val_str, max_val_str


def get_hive_columns_from_df(df: DataFrame) -> str:
    """Get name of columns with data type, compatible with hive column."""
    columns = []
    for _, schema in enumerate(df.schema.fields):
        raw_schema = schema.simpleString()
        _s = raw_schema.split(":", maxsplit=1)
        columns.append(f"`{_s[0]}` {_s[1]}")
    return ",\n".join(columns)


def is_column_safe_to_alter(
    current_dtype: StructField,
    to_be_dtype: StructField,
) -> bool:
    """Check compatibility of changing data type for Iceberg.

    References:
        - https://iceberg.apache.org/docs/latest/spark-ddl/#alter-table-alter-column
    """
    from pyspark.sql.types import (
        DecimalType,
        DoubleType,
        FloatType,
        IntegerType,
        LongType,
    )

    if current_dtype.__class__ != to_be_dtype.__class__:
        return False

    is_safe_update = False
    _current = current_dtype.dataType
    _change = to_be_dtype.dataType
    if isinstance(_current, IntegerType) and isinstance(_change, LongType):
        is_safe_update = True
    elif isinstance(_current, FloatType) and isinstance(_change, DoubleType):
        is_safe_update = True
    elif isinstance(_current, DecimalType) and isinstance(_change, DecimalType):
        current_value = regex_by_group(
            text=_current.jsonValue(), regex=r"\d+,\d+", n=0
        )
        target_value = regex_by_group(
            text=_change.jsonValue(), regex=r"\d+,\d+", n=0
        )

        current_precision, current_scale = current_value.split(",")
        target_precision, target_scale = target_value.split(",")
        if (
            int(target_precision) > int(current_precision)
            and current_scale == target_scale
        ):
            is_safe_update = True
    return is_safe_update
