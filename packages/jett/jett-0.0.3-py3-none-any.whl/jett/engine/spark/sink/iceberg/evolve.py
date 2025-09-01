from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.types import StructField, StructType

from .....utils import clean_string
from ...schema_change import (
    clean_col_except_item_from_extract_array,
    evaluate_schema_change,
    summarize_changes,
)
from ...utils import (
    column_has_only_null_or_empty_array,
    remove_column_from_struct,
    replace_column_dtype_in_nested_schema,
)
from .utils import (
    clean_hidden_partition,
    extract_hidden_partition,
    gen_alter_cols,
    gen_alter_partitions,
    get_table_partition_columns,
    is_column_safe_to_alter,
)

logger = logging.getLogger("jett")


class EvolverModel(BaseModel):
    """Iceberg Table Evolver, A Class for Evolution of Iceberg Table Schema and
    Partition.
    """

    database: str = Field(description="A database name.")
    table_name: str = Field(description="A table name.")
    schema_evolve_behavior: Literal["trust_source", "append", "trust_sink"] = (
        Field(
            description="behavior of how to evolve schema, please see IcebergModel"
        )
    )
    allow_evolve_with_missing_columns: bool = Field(
        default=False,
        description=(
            "a boolean flag, if True, the workflow will not reject when they "
            "found missing column and continue to evolve the schema"
        ),
    )
    allow_cast_safe_dtype: bool = Field(
        default=False,
        description=(
            "a boolean flag, if True, it allows to change data type of "
            "compatible columns (e.g. int (column in df) can be converted "
            "into double (column in table))"
        ),
    )
    partition_by: list[str] = Field(default_factory=list)


class Evolver:

    def __init__(
        self,
        model: EvolverModel,
        *,
        df: DataFrame,
        spark: SparkSession,
    ) -> None:
        self.model: EvolverModel = model
        self.df: DataFrame = df
        self.spark: SparkSession = spark

        # NOTE: Set internal arguments
        self.is_schema_diff: bool = False
        self.is_table_schema_changed: bool = False
        self.is_partition_diff: bool = False
        self.is_table_partition_changed: bool = False
        self.current_partition_spec: list[str] = []
        self.transform_dict_safe_cast: dict[str, StructField] = {}
        self.detailed_changes: list[dict] = []
        self.list_sql_alter: list[str] = []

        self.transform_schema_to_drop: list[str] = []
        self.transform_schema_after_drop: StructType | None = None

    def __execute_add_column(self, to_add_col_cmds):
        logger.info("total new columns: %s", len(to_add_col_cmds))
        to_add_cols_cmd_str = ",\n".join(to_add_col_cmds)
        add_new_cols_stmt = f"""
        ALTER TABLE {self.model.database}.{self.model.table_name}
        ADD COLUMNS (
        {to_add_cols_cmd_str}
        )
        """
        add_new_cols_stmt = clean_string(text=add_new_cols_stmt)
        logger.info(add_new_cols_stmt)
        self.list_sql_alter.append(add_new_cols_stmt)
        self.spark.sql(add_new_cols_stmt)

    def __execute_alter_column(self, to_alter_col_cmds):
        # see column types that Iceberg can covert type safely
        # https://iceberg.apache.org/docs/latest/spark-ddl/#alter-table-alter-column
        logger.info(
            "total columns to be changed data type: %s", len(to_alter_col_cmds)
        )
        for cmd in to_alter_col_cmds:
            alter_col_stmt = (
                f"ALTER TABLE {self.model.database}.{self.model.table_name} "
                f"ALTER COLUMN {cmd}"
            )
            logger.info(alter_col_stmt)
            self.list_sql_alter.append(alter_col_stmt)
            self.spark.sql(alter_col_stmt)

    def __execute_drop_column(self, to_drop_col_cmds):
        logger.info("total columns to be dropped: %s", len(to_drop_col_cmds))
        for cmd in to_drop_col_cmds:
            drop_col_stmt = (
                f"ALTER TABLE {self.model.database}.{self.model.table_name} "
                f"DROP COLUMN {cmd}"
            )
            logger.info(drop_col_stmt)
            self.list_sql_alter.append(drop_col_stmt)
            self.spark.sql(drop_col_stmt)

    def _evolve_schema_trust_source(
        self,
        to_add_col_cmds: list[str],
        to_alter_col_cmds: list[str],
        to_drop_col_cmds: list[str],
    ) -> None:
        """
        Alter table columns, based on new schema from source DataFrame
        The function supports 3 operations, which are
        1. alter type of columns
        2. add new columns
        3. and drop columns
        """

        if len(to_alter_col_cmds) > 0:
            self.__execute_alter_column(to_alter_col_cmds)

        if len(to_add_col_cmds) > 0:
            self.__execute_add_column(to_add_col_cmds)

        if len(to_drop_col_cmds) > 0:
            self.__execute_drop_column(to_drop_col_cmds)

        if (
            len(to_alter_col_cmds) > 0
            or len(to_add_col_cmds) > 0
            or len(to_drop_col_cmds) > 0
        ):
            self._is_table_schema_changed = True

        logger.info("schema change completed")

    def _evolve_schema_append(
        self,
        to_add_col_cmds: list[str],
        to_alter_col_cmds: list[str],
        to_drop_col_cmds: list[str],
    ) -> None:
        """
        Alter table columns, based on new schema from source Dataframe
        The function supports only 2 operations, which are
        1. alter type of columns
        2. add new columns
        Because of append mode doesn't allow to remove or drop any column or field
        """

        if self.model.allow_evolve_with_missing_columns:
            if len(to_alter_col_cmds) > 0:
                self.__execute_alter_column(to_alter_col_cmds)

            if len(to_add_col_cmds) > 0:
                self.__execute_add_column(to_add_col_cmds)
        else:
            if len(to_drop_col_cmds) > 0:
                missing_cols = "\n".join(to_drop_col_cmds)
                raise RuntimeError(
                    f"please add the missing columns: {missing_cols}"
                )

            if len(to_alter_col_cmds) > 0:
                self.__execute_alter_column(to_alter_col_cmds)

            if len(to_add_col_cmds) > 0:
                self.__execute_add_column(to_add_col_cmds)

        if len(to_alter_col_cmds) > 0 or len(to_add_col_cmds) > 0:
            self._is_table_schema_changed = True

        logger.info("schema change completed")

    def _set_transform_details_for_safe_column_change_dtype(
        self,
        current_dtype: StructField,
        to_be_dtype: StructField,
        parent_cols: list[str],
    ) -> None:
        """Set the transform dict for columns that are safe to be change data
        type.
        """
        from pyspark.sql.types import StructField, StructType

        if len(parent_cols) > 0:
            root_column = parent_cols[0]
            root_schema = self.df.select(root_column).schema[0]
            if root_column in self.transform_dict_safe_cast.keys():
                root_schema = self.transform_dict_safe_cast[root_column]

            target_column = None
            to_dtype = current_dtype
            if isinstance(to_be_dtype, StructField):
                target_column = to_be_dtype.name
                to_dtype = current_dtype.dataType

            replaced_schema = replace_column_dtype_in_nested_schema(
                schema=root_schema,
                parent_cols=parent_cols.copy(),
                target_column=target_column,
                to_dtype=to_dtype,
            )
        else:
            root_column = current_dtype.name
            replaced_schema = current_dtype

        self.transform_dict_safe_cast[root_column] = replaced_schema

        # set schema for drop columns, used in method _is_column_contain_only_null_or_empty_array
        if self.transform_schema_after_drop is None:
            self.transform_schema_after_drop = self.df.schema

        json_schema = self.transform_schema_after_drop.jsonValue()
        to_fixed_index = [
            i
            for i, field in enumerate(json_schema["fields"])
            if field["name"] == root_column
        ][0]
        json_schema["fields"][to_fixed_index] = replaced_schema.jsonValue()
        self.transform_schema_after_drop = StructType.fromJson(json_schema)

    def _is_column_safe_to_be_changed_dtype(
        self,
        current_dtype,
        to_be_dtype,
        parent_cols: list[str],
    ) -> bool:
        """
        check compatibility of changing data type for common cases
        support cases are
        - cast integer to double
        - cast integer to float
        - cast integer to bigint
        note: current_dtype is the current column's data type in the table
              to_be_dtype is the column's data type in the dataframe
        """
        from pyspark.sql.types import (
            DoubleType,
            FloatType,
            IntegerType,
            LongType,
            StructField,
        )

        is_safe_update = False
        _cur_dtype = current_dtype
        _tobe_dtype = to_be_dtype
        if isinstance(current_dtype, StructField):
            _cur_dtype = current_dtype.dataType
            _tobe_dtype = to_be_dtype.dataType

        if isinstance(_tobe_dtype, IntegerType):
            if isinstance(_cur_dtype, DoubleType):
                is_safe_update = True
            elif isinstance(_cur_dtype, FloatType):
                is_safe_update = True
            elif isinstance(_cur_dtype, LongType):
                is_safe_update = True

            # _cur_dtype is DecimalType, this will not support due to not know the precision and scale
            # it can cause null value after cast if scale is small

        if is_safe_update:
            self._set_transform_details_for_safe_column_change_dtype(
                current_dtype=current_dtype,
                to_be_dtype=to_be_dtype,
                parent_cols=parent_cols,
            )

        return is_safe_update

    def _is_column_contain_only_null_or_empty_array(
        self,
        to_be_dtype,
        parent_cols: list[str],
    ) -> bool:
        """
        check that the given column contain only null value or empty array or not
        if it's empty array, append the column to the list and wait for drop column operation
        """
        from pyspark.sql.types import ArrayType, StructField, StructType

        is_safe_update = False

        # allow to check only primitive type
        if isinstance(to_be_dtype, (StructType, ArrayType)):
            return is_safe_update

        columns = parent_cols.copy()
        if isinstance(to_be_dtype, StructField):
            columns.append(to_be_dtype.name)
            columns_str = ".".join(columns)
        else:
            # primitive type, remove last column which is element
            columns_str = ".".join(columns[:-1])

        column_without_element = clean_col_except_item_from_extract_array(
            columns=columns
        )
        is_safe_update = column_has_only_null_or_empty_array(
            df=self.df, column=".".join(column_without_element)
        )
        if is_safe_update:
            schema = self.transform_schema_after_drop
            if schema is None:
                schema = self.df.schema

            self.transform_schema_after_drop = remove_column_from_struct(
                schema=schema, column=columns_str
            )
            self.transform_schema_to_drop.append(columns_str)

        return is_safe_update

    def validate_column_changes_compatibility(self) -> None:
        """validate the compatibility of columns changes before alter operation."""
        disallow_changes_unsafe_alter = []
        for s in self.detailed_changes:
            change_type = s.get("type")
            target_struct_type = s.get("target_struct_type", None)
            source_struct_type = s.get("source_struct_type", None)
            parent_cols = s.get("parent_cols", [])

            if change_type == "alter_col":
                is_safe_update = is_column_safe_to_alter(
                    current_dtype=target_struct_type,
                    to_be_dtype=source_struct_type,
                )
                if is_safe_update is False and self.model.allow_cast_safe_dtype:
                    is_safe_update = self._is_column_safe_to_be_changed_dtype(
                        current_dtype=target_struct_type,
                        to_be_dtype=source_struct_type,
                        parent_cols=parent_cols,
                    )
                if (
                    is_safe_update is False
                    and self.model.allow_evolve_with_missing_columns
                ):
                    is_safe_update = (
                        self._is_column_contain_only_null_or_empty_array(
                            to_be_dtype=source_struct_type,
                            parent_cols=parent_cols,
                        )
                    )

                if not is_safe_update:
                    disallow_changes_unsafe_alter.append(s)

        if len(disallow_changes_unsafe_alter) > 0:
            _errors = []
            for s in disallow_changes_unsafe_alter:
                parent_col = ".".join(s["parent_cols"])
                source_str = s["source_struct_type"].simpleString()
                target_str = s["target_struct_type"].simpleString()
                _error = f"from {target_str} to {source_str}"
                if parent_col != "":
                    _error = f"{_error} (parent column={parent_col})"
                _errors.append(_error)
            err = "\n".join(_errors)
            raise RuntimeError(
                f"found unsafe columns to be altered data type\n{err}"
            )

    def fetch_detailed_changes(self) -> list[dict]:
        """Wrapper of evaluate_schema_change function that use for getting
        detailed changes of each different column or field from DataFrame schema
        compare to table schema.
        """
        source_schema: StructType = self.df.schema
        table_schema: StructType = self.spark.sql(
            f"SELECT * FROM {self.model.database}.{self.model.table_name} "
            f"LIMIT 0"
        ).schema
        return evaluate_schema_change(
            src_schema=source_schema,
            tgt_schema=table_schema,
        )

    def evolve_schema(self) -> None:
        """Evolve table schema based on incoming dataframe and evolve behavior."""
        from pyspark.sql.functions import col

        logger.info(
            f"Schema evolve behavior: {self.model.schema_evolve_behavior}"
        )
        table_schema = self.spark.sql(
            f"SELECT * FROM {self.model.database}.{self.model.table_name}"
        ).schema
        schema_diff: bool = self.df.schema != table_schema
        logger.info(f"schema diff: {schema_diff}")
        if schema_diff:
            self.is_schema_diff = True
            self.detailed_changes = self.fetch_detailed_changes()
            if len(self.detailed_changes) == 0:
                logger.info(
                    "schema does not change, only nullable or metadata of "
                    "schema is difference, skip evolution"
                )
                return

            logger.info("Validate changes of columns")
            self.validate_column_changes_compatibility()

            # cast data type for compatible type change
            if len(self.transform_dict_safe_cast) > 0:
                logger.info(
                    "found %s columns that are safe to be changed their own data type",
                    len(self.transform_dict_safe_cast),
                )
                logger.info("apply cast data type for safe columns")
                _transform_dict = {}
                for k, v in self.transform_dict_safe_cast.items():
                    _transform_dict[k] = col(k).cast(v.dataType)
                    logger.info(
                        "target col: %s, cast as: %s",
                        k,
                        v.dataType.simpleString(),
                    )
                self.df = self.df.withColumns(_transform_dict)

            if len(self.transform_schema_to_drop) > 0:
                logger.info(
                    "found %s columns contain only null or empty array",
                    len(self.transform_schema_to_drop),
                )
                logger.info(
                    "affected columns (dropped from df): %s",
                    ", ".join(self.transform_schema_to_drop),
                )
                self.df = self.df.to(self.transform_schema_after_drop)

            # NOTE: Refresh the changes
            self.detailed_changes = self.fetch_detailed_changes()
            match self.model.schema_evolve_behavior:
                case "trust_source":
                    logger.info("evolve schema based on source dataframe")
                    self._evolve_schema_trust_source(
                        *gen_alter_cols(changes=self.detailed_changes)
                    )
                case "append":
                    logger.info(
                        "append schema only (add new columns and alter columns)"
                    )
                    self._evolve_schema_append(
                        *gen_alter_cols(changes=self.detailed_changes)
                    )

    def apply_alter(self, proc: list[str]):
        for p in proc:
            logger.info(f"Apply: {p}")
            self.list_sql_alter.append(p)
            self.spark.sql(p)

    def evolve_partition(self) -> None:
        """Evolve partition."""
        self.current_partition_spec = get_table_partition_columns(
            spark=self.spark,
            db_name=self.model.database,
            table_name=self.model.table_name,
        )
        _source = [
            clean_hidden_partition(partition_spec=p)
            for p in self.model.partition_by
        ]
        _table = [
            clean_hidden_partition(partition_spec=p)
            for p in self.current_partition_spec
        ]
        partition_diff: bool = sorted(_source) != sorted(_table)
        logger.info(f"partition diff: {partition_diff}")
        if not partition_diff:
            return

        self.is_partition_diff = True
        logger.info("evolve partition")
        logger.info(
            f"Current table partition spec: {self.current_partition_spec}"
        )
        logger.info(f"new partition specification: {self.model.partition_by}")
        to_add, to_replace, to_drop = gen_alter_partitions(
            database=self.model.database,
            table_name=self.model.table_name,
            source_partition=extract_hidden_partition(self.model.partition_by),
            table_partition=extract_hidden_partition(
                self.current_partition_spec
            ),
        )

        if to_drop:
            logger.info(f"total partitions to be dropped: {len(to_drop)}")
            self.apply_alter(to_drop)

        if to_replace:
            logger.info(
                f"total existing partitions to be replaced: {len(to_replace)}"
            )
            self.apply_alter(to_replace)

        if to_add:
            logger.info(f"total new partitions: {len(to_add)}")
            self.apply_alter(to_add)

        self.is_table_partition_changed = True
        logger.info("partition is evolved successfully")

    def get_simple_detail_changes(
        self,
    ) -> tuple[list[dict], list[dict], list[dict]]:
        """
        get summarize of column changes
        """
        alter_list, add_list, drop_list = summarize_changes(
            changes=self.detailed_changes
        )
        if self.model.allow_evolve_with_missing_columns:
            drop_list = []
        if self.model.allow_cast_safe_dtype:
            alter_list = []
        return alter_list, add_list, drop_list
