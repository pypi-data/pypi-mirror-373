from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, SparkSession
    from pyspark.sql.connect.session import DataFrame as DataFrameRemote

    from ..sink import Sink

    PairCol = tuple[Column, str]
    AnyDataFrame = DataFrame | DataFrameRemote
    AnyApplyGroupOutput = PairCol | list[PairCol]
    AnyApplyOutput = AnyApplyGroupOutput | AnyDataFrame

from pydantic import Field

from ....__types import DictData
from ....errors import ToolTransformError
from ....utils import dt2str
from ..schema_change import (
    ENUM_EXTRACT_ARRAY_TYPE,
    evaluate_schema_change,
)
from ..utils import (
    get_simple_str_dtype,
    is_root_level_column_primitive_type,
    is_table_exist,
)
from .__abc import BaseSparkTransform

logger = logging.getLogger("jett")


class CalculateMinMaxOfColumns(BaseSparkTransform):
    """Calculate Min Max of Columns operator transform model."""

    op: Literal["calculate_min_max_of_columns"]
    columns: list[str] = Field()

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> AnyApplyOutput:
        """Apply to Calculate the minimum and maximum values of given columns
        only support root level column and primitive type and result is stored
        in metric transform.
        """
        exception_group: list[str] = []
        for column in self.columns:
            is_safe = is_root_level_column_primitive_type(
                schema=df.schema, column=column
            )
            if not is_safe:
                exception_group.append(
                    f"{column} is not root level column and not primitive type"
                )

        if len(exception_group) != 0:
            raise ToolTransformError(
                f"failed to validate properties: {exception_group}",
            )

        logger.info("calculate min and max of columns")
        _temp_view_name = "temp_view_calculate_min_max_of_columns"
        clauses = []
        for column in self.columns:
            clauses.append(f"MIN({column}) AS __min__{column}")
            clauses.append(f"MAX({column}) AS __max__{column}")
        clauses = ", ".join(clauses)

        df.createOrReplaceTempView(_temp_view_name)
        collected_data = spark.sql(
            f"SELECT {clauses} FROM {_temp_view_name}"
        ).collect()
        collected_data = collected_data[0].asDict()

        results_dict = {}
        for k, v in collected_data.items():
            _column = k.replace("__min__", "").replace("__max__", "")
            _key_dict = "min_value" if "min" in k else "max_value"
            _value = v
            if isinstance(_value, datetime):
                _value = dt2str(
                    _value,
                    sep="T",
                    timespec="milliseconds",
                    add_utc_suffix=True,
                )

            updated_dict = {_key_dict: _value}
            if _column in results_dict.keys():
                old_dict = results_dict[_column]
                updated_dict.update(old_dict)
            results_dict[_column] = updated_dict

        results = []
        for k, v in results_dict.items():
            v.update({"column": k})
            results.append(v)
            logger.info(
                "column: %s, min value: %s, max value: %s",
                k,
                v.get("min_value"),
                v.get("max_value"),
            )
        result = {"results": results}
        return result


class DetectSchemaChangeWithSink(BaseSparkTransform):
    op: Literal["detect_schema_change_with_sink"]
    sink_type: str | None = None
    db_name: str | None = None
    table_name: str | None = None
    allow_table_not_exist: bool = False

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> AnyApplyOutput:
        """Detect schema change between DF and table schema."""
        from pyspark.sql.types import ArrayType, StructField

        sql: str = "SELECT * FROM {database}.{table_name} LIMIT 0"
        logger.info("detect schema change with sink")
        if self.sink_type is not None:
            logger.info("use sink's configuration from model")
            db_name = self.db_name
            table_name = self.table_name
        else:
            logger.info("use sink's configuration from config dict")
            _sink: Sink = engine["engine"].sink
            if _sink.type in ("iceberg",):
                db_name = _sink.database
                table_name = _sink.table_name
            else:
                raise NotImplementedError("support sink only iceberg")

        if self.allow_table_not_exist is True and not is_table_exist(
            spark=spark,
            database=db_name,
            table_name=table_name,
        ):
            logger.info("skip detect schema change due to table does not exist")
            return {
                "columns_to_drop": [],
                "columns_to_add": [],
                "columns_to_alter": [],
            }

        sql = sql.format(database=db_name, table_name=table_name)
        changes = evaluate_schema_change(
            src_schema=df.schema, tgt_schema=spark.sql(sql).schema
        )
        columns_to_drop = []
        columns_to_add = []
        columns_to_alter = []
        for change in changes:
            change_type = change["type"]
            source_struct_type = change["source_struct_type"]
            parent_column = (
                ".".join(change["parent_cols"])
                if len(change["parent_cols"]) > 0
                else None
            )

            if change_type == "add_col":
                columns_to_add.append(
                    {
                        "column_name": source_struct_type.name,
                        "dtype": source_struct_type.dataType.simpleString(),
                        "add_after_column": change["add_col_after"],
                        "parent_column": parent_column,
                    }
                )
            elif change_type == "drop_col":
                columns_to_drop.append(
                    {
                        "column_name": source_struct_type.name,
                        "dtype": source_struct_type.dataType.simpleString(),
                        "parent_column": parent_column,
                    }
                )
            elif change_type == "alter_col":
                _parent_cols = change["parent_cols"]
                from_dtype = get_simple_str_dtype(change["target_struct_type"])
                to_dtype = get_simple_str_dtype(source_struct_type)

                if isinstance(source_struct_type, ArrayType) or not isinstance(
                    source_struct_type, StructField
                ):
                    column_name = _parent_cols.pop()
                    if column_name == ENUM_EXTRACT_ARRAY_TYPE:
                        column_name = _parent_cols.pop()
                else:
                    column_name = source_struct_type.name

                if len(_parent_cols) == 0:
                    _parent_cols = None

                columns_to_alter.append(
                    {
                        "column_name": column_name,
                        "from_dtype": from_dtype,
                        "to_dtype": to_dtype,
                        "parent_column": _parent_cols,
                    }
                )

        if len(columns_to_drop) > 0:
            logger.info(
                "found missing %s columns from dataframe", len(columns_to_drop)
            )
            for text in columns_to_drop:
                logger.info(text)

        if len(columns_to_add) > 0:
            logger.info(
                "found %s new columns in dataframe", len(columns_to_add)
            )
            for text in columns_to_add:
                logger.info(text)

        if len(columns_to_alter) > 0:
            logger.info(
                "found %s columns have data type's change",
                len(columns_to_alter),
            )
            for text in columns_to_alter:
                logger.info(text)
        return {
            "columns_to_drop": columns_to_drop,
            "columns_to_add": columns_to_add,
            "columns_to_alter": columns_to_alter,
        }
