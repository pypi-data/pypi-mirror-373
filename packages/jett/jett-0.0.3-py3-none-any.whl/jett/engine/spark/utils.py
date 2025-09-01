from __future__ import annotations

import copy
import logging
import re
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.connect.session import SparkSession as SparkRemoteSession
    from pyspark.sql.types import DataType, StructField, StructType

from ...utils import handle_command, is_snake_case

logger = logging.getLogger("jett")

ENUM_EXTRACT_ARRAY_TYPE: Final[str] = "__array_element"
ALLOW_VALIDATE_PATTERNS: Final[tuple[str, ...]] = (
    "non_snake_case",
    "whitespace",
)


def schema2dict(
    schema: StructType, sorted_by_name: bool = False
) -> list[dict[str, str]]:
    """Convert StructType object to dict that include keys, `name` and `dtype`.

    Args:
        schema:
        sorted_by_name:
    """
    rs: list[dict[str, str]] = [
        {"name": c.name, "dtype": c.dataType.simpleString()} for c in schema
    ]
    return sorted(rs, key=lambda x: x["name"]) if sorted_by_name else rs


def is_remote_session(spark: SparkSession | SparkRemoteSession) -> bool:
    """Check whether given session is remote session or not."""
    from pyspark.sql.connect.session import SparkSession as SparkRemoteSession

    return isinstance(spark, SparkRemoteSession)


def yarn_kill(app_id: str) -> None:
    """Kill spark application on YARN."""
    kill_cmd: str = f"yarn application -kill {app_id}"
    for line in handle_command(cmd=kill_cmd):
        logger.info(line.strip())


def yarn_fetch_log(application_id: str, log_file: str) -> None:
    """Fetch the YARN application log (stdout and stderr)."""
    fetch_cmd: str = (
        f"yarn logs -applicationId {application_id} -log_files {log_file}"
    )
    for line in handle_command(cmd=fetch_cmd):
        logger.info(line.strip())


def extract_spark_conf_keys(cmd: list[str]) -> list[str]:
    """Extract spark conf keys from existing list of submit commands."""
    return [
        c.split("=")[0].replace("'", "").replace('"', "")
        for c in cmd
        if "=" in c and len(c) > 1 and c.count("=") == 1
    ]


def clean_tz_for_extra_java_options(option: str, tz: str) -> str:
    """Clean and set time zone in extraJavaOptions"""
    java_user_timezone_key: str = "user.timezone"
    options: list[str] = [
        p.strip()
        for p in option.split("-D")
        if java_user_timezone_key not in p.split("=")[0]
    ]
    options = list(filter(None, options))
    options.append(f"{java_user_timezone_key}={tz}")
    options = [f"-D{p}" for p in options]
    return " ".join(options)


def add_spark_cmd(
    cmd: list[str], key: str, value: str | int | list[str] | None
) -> list[str]:
    """Extend Spark command that generate after checking value is not empty."""
    if value is None:
        return cmd

    if isinstance(value, list) and len(value) != 0:
        value_str: str = ",".join(value)
        cmd.extend([f"--{key}", f'"{value_str}"'])
    elif isinstance(value, str):
        cmd.extend([f"--{key}", value])
    elif isinstance(value, int):
        cmd.extend([f"--{key}", str(value)])

    return cmd


def has_fix_array_index(input_str: str) -> bool:
    """Check that string contains bracket, `[{number}]`, or not

    Examples:
        contains case: items[0], items[322]
    """
    return re.search(r"\[\d+]", input_str) is not None


def replace_fix_array_index_with_x_index(input_str: str) -> str:
    """Replace any existing string like `[{number}]` with [x]

    Examples:
        input:
            >>> "items[0].detail[322].name"
        output:
            >>> "items[x].detail[x].name"
    """
    return re.sub(r"\[\d+]", "[x]", input_str)


def extract_cols_selectable(schema: StructType, prefix: str = "") -> list[str]:
    """Extracts all selectable columns of given schema, support all top level
    column and nested column and array column.

    Returns:
        list[str]: All cols like:
            ["c1", "c2.f1", "c2.f2", "c3"]

    Examples:
        Input:
        >>> from pyspark.sql.types import StringType, IntegerType, DoubleType
        >>> StructType(
        ...     [
        ...         StructField("texts", ArrayType(StringType())),
        ...         StructField("items", ArrayType(StructType(
        ...             [
        ...                 StructField("name", StringType()),
        ...                 StructField("price", IntegerType()),
        ...                 StructField("detail", ArrayType(StructType(
        ...                     [
        ...                         StructField("field1", StringType()),
        ...                         StructField("field2", DoubleType()),
        ...                     ]
        ...                 )))
        ...             ]
        ...         )))
        ...     ]
        ... )

        Output:
        >>> [
        ...     'texts',
        ...     'texts[x]',
        ...     'items',
        ...     'items[x]',
        ...     'items[x].name',
        ...     'items[x].price',
        ...     'items[x].detail',
        ...     'items[x].detail[x]',
        ...     'items[x].detail[x].field1',
        ...     'items[x].detail[x].field2',
        ... ]
    """
    from pyspark.sql.types import ArrayType, StructType

    rs: list[str] = []
    for field in schema:
        rs.append(prefix + field.name)
        field_type = field.dataType
        if isinstance(field_type, StructType):
            rs.extend(
                extract_cols_selectable(field_type, f"{prefix}{field.name}.")
            )
        elif isinstance(field_type, ArrayType):
            rs.append(prefix + field.name + "[x]")
            if isinstance(field_type.elementType, StructType):
                rs.extend(
                    extract_cols_selectable(
                        field_type.elementType, f"{prefix}{field.name}[x]."
                    )
                )
    return rs


def replace_all_occurrences(input_str: str, old: str, new: str) -> str:
    """Replace all occurrences of a specific string (case-insensitive) with a
    given string.
    """
    return re.sub(re.escape(old), new, input_str, flags=re.IGNORECASE)


def is_table_exist(
    spark: SparkSession | SparkRemoteSession,
    database: str,
    table_name: str,
) -> bool:
    """Check table's existence."""
    catalog = spark.catalog.currentCatalog()
    return spark.catalog.tableExists(f"{catalog}.{database}.{table_name}")


def is_database_exist(
    spark: SparkSession | SparkRemoteSession, database: str
) -> bool:
    """Check database's existence."""
    return spark.catalog.databaseExists(dbName=database)


def extract_cols_without_array(schema: StructType) -> list[str]:
    """Extract selectable columns without array type.

        It returns only list of selectable columns that are not nested array
    type return only root array column name.

    Args:
        schema (StructType):

    Returns:
        list[str]: A list of column name that extract by selectable without
            array type.
    """
    selectable_cols: list[str] = extract_cols_selectable(schema=schema)
    nested_array_cols: list[str] = [c for c in selectable_cols if "[x]" in c]
    final_selectable_cols: list[str] = [
        c for c in selectable_cols if c not in nested_array_cols
    ]

    rs: list[str] = []
    for c in final_selectable_cols:
        not_parent: bool = True
        for fc in final_selectable_cols:
            if fc != c and fc.startswith(f"{c}."):
                not_parent: bool = False

        if not_parent:
            rs.append(c)
    return rs


def extract_col_with_pattern(
    schema: StructType,
    patterns: list[str],
    parent_cols: list[str] | None = None,
) -> list[str]:
    """Do recursive find the colum name that does not follow the pattern
    current supported patterns are non_snake_case and whitespace
    """
    from pyspark.sql.types import ArrayType, StructType

    parent_cols: list[str] = parent_cols or []

    def _validate_and_append_error(
        col_name: str,
        p_cols: list[str],
        e_cols: list[str],
        pt: list[str],
    ) -> list[str]:
        """Child Wrapped function for extract_pyspark_column_names_with_pattern
        validate snake case or whitespace and append error columns

        Args:
            col_name:
            p_cols: A parent columns
            e_cols: An error columns
            pt:
        """
        is_found_err: bool = False
        for pattern in pt:
            if pattern == "non_snake_case" and not is_snake_case(col_name):
                is_found_err = True
            elif pattern == "whitespace" and " " in col_name:
                is_found_err = True

        if is_found_err:
            error_col = (
                col_name
                if len(p_cols) == 0
                else ".".join(p_cols) + f".{col_name}"
            )
            e_cols.append(error_col)

        return e_cols

    if all(p not in ALLOW_VALIDATE_PATTERNS for p in patterns):
        raise ValueError(
            f"patterns must contain value in {ALLOW_VALIDATE_PATTERNS}"
        )

    error_cols: list[str] = []

    for column in schema:
        if isinstance(column.dataType, ArrayType):
            if isinstance(column.dataType.elementType, StructType):
                _parent_cols = copy.deepcopy(parent_cols)
                _parent_cols.append(column.name)
                error_cols = error_cols + extract_col_with_pattern(
                    schema=column.dataType.elementType,
                    patterns=patterns,
                    parent_cols=_parent_cols,
                )
            else:
                error_cols = _validate_and_append_error(
                    col_name=column.name,
                    p_cols=parent_cols,
                    e_cols=error_cols,
                    pt=patterns,
                )
        elif isinstance(column.dataType, StructType):
            _parent_cols = copy.deepcopy(parent_cols)
            _parent_cols.append(column.name)
            error_cols = error_cols + extract_col_with_pattern(
                schema=column.dataType,
                patterns=patterns,
                parent_cols=_parent_cols,
            )
        else:
            error_cols = _validate_and_append_error(
                col_name=column.name,
                p_cols=parent_cols,
                e_cols=error_cols,
                pt=patterns,
            )
    return error_cols


def validate_col_disallow_pattern(
    schema: StructType, patterns: list[str]
) -> None:
    """Validate columns names in dataframe (support nested schema) from the
    pattern.
    """
    if all(p not in ALLOW_VALIDATE_PATTERNS for p in patterns):
        raise ValueError(
            f"Patterns must contain value in {ALLOW_VALIDATE_PATTERNS}"
        )

    error_cols = extract_col_with_pattern(schema=schema, patterns=patterns)
    if len(error_cols) > 0:
        cols: str = ", ".join(error_cols)
        raise ValueError(
            f"Please check column naming convention (must not be {patterns!r}) "
            f"on columns: {cols}"
        )


def validate_col_allow_snake_case(schema: StructType) -> None:
    """Validate columns, allow only snake case."""
    validate_col_disallow_pattern(schema=schema, patterns=["non_snake_case"])


def get_simple_str_dtype(dtype: DataType | StructField) -> str:
    """Get pyspark data type in simple string format."""
    from pyspark.sql.types import StructField

    return (
        dtype.dataType.simpleString()
        if isinstance(dtype, StructField)
        else dtype.simpleString()
    )


def is_root_level_column(schema: StructType, column: str) -> bool:
    """Return True if it is a column root level column."""
    for schema_col in schema:
        if schema_col.name == column:
            return True
    return False


def is_root_level_column_primitive_type(
    schema: StructType, column: str
) -> bool:
    """is a column is a root level column and also a primitive type."""
    from pyspark.sql.types import ArrayType, StructType

    is_root_column = is_root_level_column(schema=schema, column=column)
    if not is_root_column:
        return is_root_column

    for schema_col in schema:
        if schema_col.name == column and not isinstance(
            schema_col.dataType, (ArrayType, StructType)
        ):
            return True
    return False


def _extract_selectable_plan_with_auto_explode(
    schema: DataType,
    columns: list[str],
    select_columns: list[str] | None = None,
    plans: list[dict] | None = None,
) -> list[dict]:
    """A child function for method `select_with_auto_explode`
    extract the plan of select and explode based on the given schema.

    Args:
        schema (DataType):
        columns (list[str]):
        select_columns:
        plans:
    """
    from pyspark.sql.types import ArrayType, StructType

    select_columns: list[str] = select_columns or []
    plans: list[dict] = plans or []

    if len(columns) == 0:
        if len(select_columns) > 0:
            plans.append(
                {"action": "select", "columns": ".".join(select_columns)}
            )
        return plans

    if not isinstance(schema, StructType):
        raise ValueError("schema mismatch, schema must be StructType")

    current_column = columns.pop(0)
    current_field = [s for s in schema if s.name == current_column]
    if len(current_field) == 0:
        raise ValueError(
            f"not found column {current_column} in current struct {schema.simpleString()}"
        )

    current_field = current_field[0]
    child_field = current_field.dataType
    if isinstance(current_field.dataType, ArrayType) and len(columns) > 0:
        if len(select_columns) > 0:
            select_columns.append(current_column)
            plans.append(
                {"action": "select", "columns": ".".join(select_columns)}
            )
            select_columns = []

        if len(columns) > 0:
            plans.append(
                {
                    "action": "explode",
                    "columns": current_column,
                    "alias": "temp_array_col",
                }
            )
            select_columns.append("temp_array_col")

        child_field = current_field.dataType.elementType
    else:
        select_columns.append(current_column)

    return _extract_selectable_plan_with_auto_explode(
        schema=child_field,
        columns=columns,
        select_columns=select_columns,
        plans=plans,
    )


def select_with_auto_explode(df: DataFrame, column: str) -> DataFrame:
    """This method does similar thing to df.select(), but it explodes array
    column automatically when the schema during column extraction is ArrayType.
    """
    from pyspark.sql.functions import explode

    plans = _extract_selectable_plan_with_auto_explode(
        schema=df.schema, columns=column.split("."), select_columns=[], plans=[]
    )
    rs_df: DataFrame = df
    for i, plan in enumerate(plans):
        _col = plan["columns"]
        if plan["action"] == "explode":
            _col = explode(_col).alias(plan["alias"])

        if i == 0:
            rs_df = df.select(_col)
        else:
            rs_df = rs_df.select(_col)
    return rs_df


def column_has_only_null_or_empty_array(df: DataFrame, column: str) -> bool:
    """
    check that the column contains only null or empty array
    cannot handle case array -> struct -> array
    """
    new_df = select_with_auto_explode(df=df, column=column)
    rows = new_df.distinct().collect()
    has_only_null_or_empty_array = True
    keywords = [None, [None], []]
    for row in rows:
        for _, v in row.asDict(True).items():
            if v not in keywords:
                has_only_null_or_empty_array = False

    return has_only_null_or_empty_array


def _child_remove_column_from_struct(
    schema_dict: dict, columns: list[str]
) -> dict:
    """A child function of remove_column_from_struct recursively extract the
    dict of pyspark schema and remove the given column.
    """
    # NOTE: remove the column
    if len(columns) == 1:
        if schema_dict["type"] != "struct":
            raise ValueError(
                f"schema must be struct, cannot delete the column {columns}"
            )

        new_fields = [
            field
            for field in schema_dict["fields"]
            if field["name"] != columns[0]
        ]
        if len(new_fields) == len(schema_dict["fields"]):
            raise ValueError(
                f"field {columns[0]} not found in current struct: {schema_dict}"
            )

        schema_dict["fields"] = new_fields
        return schema_dict

    current_column = columns.pop(0)
    index = None
    current_field = None

    if schema_dict["type"] == "struct":
        for i, field in enumerate(schema_dict["fields"]):
            if field["name"] == current_column:
                current_field = field
                index = i
                break
        if index is None:
            raise ValueError(
                f"field {current_column} not found in current schema "
                f"{schema_dict}"
            )

        if (
            current_field["type"]["type"] == "array"
            and len(columns) != 0
            and columns[0] != ENUM_EXTRACT_ARRAY_TYPE
        ):
            raise ValueError(
                f"schema mismatch, found array schema but parent field name "
                f"{columns[0]} is not {ENUM_EXTRACT_ARRAY_TYPE}"
            )

        schema_dict["fields"][index]["type"] = _child_remove_column_from_struct(
            schema_dict=current_field["type"], columns=columns
        )
    elif schema_dict["type"] == "array":
        schema_dict["elementType"] = _child_remove_column_from_struct(
            schema_dict=schema_dict["elementType"], columns=columns
        )

    return schema_dict


def remove_column_from_struct(schema: StructType, column: str) -> StructType:
    """Remove column from given schema (StructType)."""
    from pyspark.sql.types import StructType

    schema_dict = _child_remove_column_from_struct(
        schema_dict=schema.jsonValue(),
        columns=column.split("."),
    )
    return StructType.fromJson(json=schema_dict)


def _child_replace_column_dtype_in_nested_schema(
    schema_dict: dict, parent_cols: list[str], target_column: str, to_dtype: str
) -> dict:
    """A child function of replace_column_dtype_in_nested_schema recursively
    manipulate pyspark schema in JSON format replace data type from given param
    """

    def __get_index_by_field_name(schema: dict, field_name: str) -> int:
        fields = schema["fields"]
        idx = [
            i for i, field in enumerate(fields) if field["name"] == field_name
        ]
        if len(idx) == 0:
            raise ValueError(
                f"not found field {field_name} (parent col) in struct {fields}"
            )
        return idx[0]

    def __classify_schema_type(schema: dict) -> str:
        _schema_type = None
        current_schema_type = schema["type"]
        if isinstance(current_schema_type, dict):
            return "root_struct"
        elif current_schema_type == "struct":
            return "nested_struct"
        elif current_schema_type == "array":
            if isinstance(schema.get("elementType"), str):
                _schema_type = "array_primitive"
            else:
                _schema_type = "array_struct"
        return _schema_type

    if len(parent_cols) == 0:
        index = __get_index_by_field_name(
            schema=schema_dict, field_name=target_column
        )
        element = schema_dict["fields"][index]
        element["type"] = to_dtype
        schema_dict["fields"][index] = element
        return schema_dict

    first_parent_col = parent_cols.pop(0)
    schema_type = __classify_schema_type(schema=schema_dict)

    # handle case's root schema
    if schema_type == "root_struct" and schema_dict["name"] == first_parent_col:
        schema_dict["type"] = _child_replace_column_dtype_in_nested_schema(
            schema_dict=schema_dict["type"],
            parent_cols=parent_cols,
            target_column=target_column,
            to_dtype=to_dtype,
        )
        return schema_dict

    if schema_type == "array_primitive":
        schema_dict["elementType"] = to_dtype
        return schema_dict

    if schema_type == "array_struct":
        schema_dict["elementType"] = (
            _child_replace_column_dtype_in_nested_schema(
                schema_dict=schema_dict["elementType"],
                parent_cols=parent_cols,
                target_column=target_column,
                to_dtype=to_dtype,
            )
        )
        return schema_dict

    # get next struct field
    index = __get_index_by_field_name(
        schema=schema_dict, field_name=first_parent_col
    )
    schema_dict["fields"][index]["type"] = (
        _child_replace_column_dtype_in_nested_schema(
            schema_dict=schema_dict["fields"][index]["type"],
            parent_cols=parent_cols,
            target_column=target_column,
            to_dtype=to_dtype,
        )
    )
    return schema_dict


def replace_column_dtype_in_nested_schema(
    schema: StructField,
    parent_cols: list[str],
    target_column: str,
    to_dtype: DataType,
) -> StructField:
    """Replace target column to desire data type (support nested schema)."""
    from pyspark.sql.types import ArrayType, StructField, StructType

    if not isinstance(schema, StructField) or not isinstance(
        schema.dataType, (StructType, ArrayType)
    ):
        raise ValueError(
            "schema must be a struct of struct or struct of array only"
        )

    to_dtype = to_dtype.simpleString()
    if to_dtype == "bigint":
        to_dtype = "long"
    output_dict = _child_replace_column_dtype_in_nested_schema(
        schema_dict=schema.jsonValue(),
        parent_cols=parent_cols,
        target_column=target_column,
        to_dtype=to_dtype,
    )
    new_schema = StructField.fromJson(output_dict)
    return new_schema


def is_column_has_null(df: DataFrame, column: str) -> bool:
    """Check that the given column contains null value or not."""
    from pyspark.sql.functions import col

    return bool(df.filter(col(column).isNull()).first())


def is_timestamp_column(column_name: str, schema: StructType) -> bool:
    """Return true if the given column a timestamp column."""
    from pyspark.sql.types import TimestampNTZType, TimestampType

    is_timestamp_col = False
    for column in schema:
        if column.name == column_name and isinstance(
            column.dataType, (TimestampNTZType, TimestampType)
        ):
            is_timestamp_col = True
    return is_timestamp_col


def get_first_level_column_exclude_nested_struct(df: DataFrame) -> list[str]:
    """Get a list of first column level that does not have nested struct.

    Args:
        df (DataFrame): A Spark DataFrame.
    """
    columns: list[str] = []
    for c in df.schema:
        _s = c.simpleString().split(":")
        if "struct" not in _s[1]:
            columns.append(_s[0])
    return columns
