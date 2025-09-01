from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, Row, SparkSession

    from ..sink import Sink

    PairCol = tuple[Column, str]

from pydantic import Field, PrivateAttr
from pydantic.functional_validators import field_validator, model_validator
from typing_extensions import Self

from ....__types import DictData
from ....utils import get_dt_now, get_random_str_unique, to_snake_case
from ..utils import (
    extract_col_with_pattern,
    extract_cols_without_array,
    is_remote_session,
    is_table_exist,
    replace_all_occurrences,
)
from .__abc import BaseSparkTransform
from .__models import RenameColMap

logger = logging.getLogger("jett")


class Expr(BaseSparkTransform):
    """Expression Operator Transform model."""

    op: Literal["expr"]
    name: str = Field(
        description=(
            "An alias name of this output of the query expression result store."
        )
    )
    query: str = Field(description="An expression query.")

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> PairCol:
        """Apply priority transform to expression the query.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.
        """
        from pyspark.sql.functions import expr

        return expr(self.query), self.name


class SQL(BaseSparkTransform):
    """SQL Operator Transform model."""

    op: Literal["sql_transform"]
    query: str = Field(
        description=(
            "A query statement that will use on the `sql` feature. If you want "
            "to interact with the current DataFrame, you should use it with "
            "`temp_table` table on this statement."
        )
    )

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply SQL.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.

        Returns:
            DataFrame:
        """
        temp_table_name: str = f"temp_table_{get_random_str_unique()}"
        query = replace_all_occurrences(
            self.query, "temp_table", temp_table_name
        )
        df.createOrReplaceTempView(temp_table_name)
        return spark.sql(query)


class RenameSnakeCase(BaseSparkTransform):
    op: Literal["rename_snakecase"]
    allow_group_transform: bool = False

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply to Rename all columns (support nested columns) to snake case format.
        by default the schema and data when reading from source is already ordered.

        Warnings:

            this transform can result in wrong data when the order of nested
        column is not an alphabetical order. the order of 1st lv column can be
        unordered.

        Notes:
            the columns can be ordered by using the logic.
            >>> df.select(sorted(df.columns))

        Examples:
            Case of unordered nested columns
            >>> from pyspark.sql.types import StructType, StructField, BooleanType
            >>> input_schema = StructType([
            ...     StructField("parent_struct", StructType([
            ...         StructField("FIRST_KEY", BooleanType(), True),
            ...         StructField("SECOND_KEY", BooleanType(), True),
            ...         ]),
            ...         True
            ...     )
            ... ])
            >>> input_data = [{
            ...     "parent_struct": {
            ...         "SECOND_KEY": False,
            ...         "FIRST_KEY": True
            ...     }
            ... }]

            Output after renaming columns will be:
            >>> new_schema = StructType([
            ...     StructField("parent_struct", StructType([
            ...         StructField("first_key", BooleanType(), True),
            ...         StructField("second_key", BooleanType(), True),
            ...         ]),
            ...         True
            ...     )
            ... ])
            >>> new_data = [{
            ...     "parent_struct": {
            ...         "first_key": False,
            ...         "second_key": True
            ...     }
            ... }]
        """
        from pyspark.sql.functions import col

        non_snake_case_cols = extract_col_with_pattern(
            schema=df.schema, patterns=["non_snake_case"]
        )
        if len(non_snake_case_cols) == 0:
            return df

        final_cols = []
        transform_dict = {}
        df = df.select(sorted(df.columns))  # always sort columns
        for schema in df.schema:
            new_col_name = None
            temp_dict = {}

            if schema.name.islower() is False or " " in schema.name:
                new_col_name = to_snake_case(schema.name)
                temp_dict[new_col_name] = col(schema.name)

            dtype = schema.dataType.simpleString()
            if dtype.islower() is False or " " in dtype:
                new_dtype = to_snake_case(dtype)
                if len(temp_dict) > 0:
                    val = temp_dict[new_col_name]
                    temp_dict[new_col_name] = val.cast(new_dtype)
                else:
                    temp_dict[schema.name] = col(schema.name).cast(new_dtype)

            if len(temp_dict) > 0:
                transform_dict = {**transform_dict, **temp_dict}
            else:
                final_cols.append(schema.name)

        if len(transform_dict) > 0:
            non_snake_case_cols = extract_col_with_pattern(
                schema=df.schema, patterns=["non_snake_case"]
            )
            logger.info(
                "found non snake case columns: %s",
                "\n".join(non_snake_case_cols),
            )
            logger.info("rename to snake case columns")
            df = df.withColumns(transform_dict)
            final_cols = final_cols + list(transform_dict.keys())
            df = df.select(*final_cols)
        return df


class RenameColumns(BaseSparkTransform):
    """Rename Columns Transform model."""

    op: Literal["rename_columns"]
    columns: list[RenameColMap] = Field(
        description="A list of RenameColMap model."
    )
    allow_fill_null_when_col_not_exist: bool = False

    @model_validator(mode="after")
    def __allow_fill_null_rule(self) -> Self:
        """Validate each column model with allow autofill null on not-existing
        column need its data type.
        """
        if self.allow_fill_null_when_col_not_exist:
            if any(c is None for c in self.columns):
                raise ValueError(
                    "`allow_fill_null_when_col_not_exist` property must use "
                    "with `dtype` property"
                )
        return self

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> list[PairCol]:
        """Apply to Rename Column transform.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.
        """
        map_cols: list[PairCol] = []
        for c in self.columns:
            if self.allow_fill_null_when_col_not_exist:
                map_cols.append(c.get_rename_pair_fix_non_existed_by_null(df))
            else:
                map_cols.append(c.get_rename_pair())
        logger.info(f"Rename columns statement:\n{map_cols}")
        return map_cols

    def apply_group(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> PairCol | list[PairCol]:
        return self.apply(df, engine, spark=spark, **kwargs)


class SelectColumns(BaseSparkTransform):
    """Select Columns Operator transform model."""

    op: Literal["select"]
    columns: list[str]
    allow_missing: bool = False

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply to Select Column.

        Args:
            df (DataFrame): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.

        Returns:
            DataFrame: A column selected Spark DataFrame.
        """
        selection: list[str] = self.columns
        if self.allow_missing:
            selection: list[str] = [c for c in self.columns if c in df.columns]
        logger.info("Select Columns")
        for c in selection:
            logger.info(f"> - {c}")
        return df.select(*selection)


class DropColumns(BaseSparkTransform):
    op: Literal["drop_columns"]
    columns: list[str]
    allow_missing_columns: bool = False

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply drop column.

        Args:
            df (DataFrame): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.

        Returns:
            DataFrame:
        """
        current_cols = df.columns
        target_cols = self.columns
        if self.allow_missing_columns:
            target_cols = [c for c in self.columns if c in current_cols]
        return df.drop(*target_cols)


class CleanMongoJsonStr(BaseSparkTransform):
    op: Literal["clean_mongo_json_string"]
    source: str
    use_java: bool = True

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> PairCol:
        """Apply to Clean Mongo Json string.

        Args:
            df (DataFrame): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.
        """
        from pyspark.sql.functions import col, expr
        from pyspark.sql.types import StringType

        from ..udf import clean_mongo_json_udf

        func_name: str = "cleanMongoJsonString"
        if self.use_java:
            java_class_name: str = "custom.CleanMongoJsonStringUDF"
            spark.udf.registerJavaFunction(
                func_name, java_class_name, StringType()
            )
            column: Column = expr(f"{func_name}({self.source})").cast("string")
            return column, self.source
        mongo_udf = clean_mongo_json_udf(spark)
        return mongo_udf(col(self.source)), self.source


class JsonStrToStruct(BaseSparkTransform):
    """Json string to Struct Operator transform model."""

    op: Literal["json_to_struct"]
    source: str
    infer_timestamp: bool = True
    timestamp_format: str = "yyyy-MM-dd'T'HH:mm:ss[.SSS]'Z'"
    timestampntz_format: str = "yyyy-MM-dd'T'HH:mm:ss[.SSS]'Z'"
    mode: Literal["PERMISSIVE", "DROPMALFORMED", "FAILFAST"] = "FAILFAST"
    tmp_dir: str | None = Field(default=None)
    _tmp_dir: str | None = PrivateAttr(default=None)

    def override_tmp_dir(self) -> str:
        rand_str: str = get_random_str_unique(n=12)
        current_date: date = get_dt_now().date()
        self._tmp_dir: str = (
            f"{self.tmp_dir}/json_string_to_struct/{current_date}/{rand_str}"
        )
        return self._tmp_dir

    def post_apply(self, engine: DictData, **kwargs):
        """Remove temp dir after apply this operator."""
        if self._tmp_dir:
            # TODO: need to add post execute func - to clean up temporary
            #   directory
            pass

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply convert JSON string column into new pyspark dataframe.

        Args:
            df (DataFrame): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.
        """
        # NOTE: spark connect, cannot use RDD, so write to temporary instead
        if is_remote_session(spark):
            temp_dir: str = self.override_tmp_dir()
            logger.info(f"Write data to temporary dir: {temp_dir}")
            (
                df.select(self.source)
                .write.format("text")
                .mode("overwrite")
                .save(temp_dir)
            )
            reader = spark.read.format("json").option("inferSchema", True)
            if not self.infer_timestamp:
                return reader.load(temp_dir, mode=self.mode)
            return (
                reader.option("inferTimestamp", self.infer_timestamp)
                .option("timestampNTZFormat", self.timestampntz_format)
                .load(
                    temp_dir,
                    timestampFormat=self.timestamp_format,
                    mode=self.mode,
                )
            )

        # IMPORTANT: Cannot do `c[str(self.source)]` in lambda func, it will
        #   raise error.
        source_str: str = str(self.source)
        rdd_data = df.rdd.map(lambda c: c[source_str])
        reader = spark.read.option("inferSchema", True)
        if self.infer_timestamp:
            return (
                reader.option("inferTimestamp", self.infer_timestamp)
                .option("timestampNTZFormat", self.timestampntz_format)
                .json(
                    rdd_data,
                    timestampFormat=self.timestamp_format,
                    mode=self.mode,
                )
            )
        return reader.json(rdd_data, mode=self.mode)


class Scd2(BaseSparkTransform):
    """SCD Type 2 Transform operator model."""

    op: Literal["scd2"]
    merge_key: list[str]
    update_key: str
    create_key: str
    col_start_name: str = "_scd2_start_time"
    col_end_name: str = "_scd2_end_time"

    @field_validator(
        "merge_key", mode="before", json_schema_input_type=list[str] | str
    )
    def __convert_merge_key_to_dict(cls, value: Any) -> Any:
        """Convert the `merge_key` column that pass with string type to list."""
        return [value] if isinstance(value, str) else value

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply to SCD Type 2.

        This method do 4 steps:
            1: Get the target DataFrame from data warehouse (if exists)
            2: Add `_scd2_start_time` and `_scd_end_time` column to the source
                DataFrame.
                - `_scd2_start_time`:
                    - if id of the row already exist in target table,
                      _scd2_start_time will be update_key for that row
                    - if id of the row doesn't exist in target table (new record),
                      _scd2_start_time will be create_key for that row
                - `_scd2_end_time`: Defaults to NULL
            3: Update df_target._scd_end_time from null to df_source._scd2_start_time in some rows
            4: Combine both DataFrames from the step 2 and 3 together and send
                it to sink process.

        Args:
            df (DataFrame): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.

        Returns:
            Dataframe: the final dataframe that ready to write to the table
        """
        from pyspark.sql.functions import col, lit

        db_name: str | None = None
        table_name: str | None = None

        # NOTE: Check if config_dict is not empty (not {})
        _sink: Sink = engine["engine"].sink
        if _sink.type in ("iceberg", "hdfs"):
            logger.info("Use sink's configuration from config dict")
            db_name: str = _sink.database
            table_name: str = _sink.table_name
        elif _sink.type.startswith("local"):
            raise NotImplementedError("Does not support local sink type.")
        else:
            logger.info(
                "No `db_name` and `table_name` provided. so no need to connect to "
                "target table and just add the _scd2_start_time and "
                "_scd2_end_time to source df"
            )
        if (
            db_name
            and table_name
            and is_table_exist(
                spark=spark, database=db_name, table_name=table_name
            )
        ):
            # Step01: get df_tgt
            tgt_df = spark.sql(f"SELECT * FROM {db_name}.{table_name}").filter(
                col(self.col_end_name).isNull()
            )
            # Step02: add _scd2_start_time and _scd_end_time column to df_source
            src_df = self._add_start_and_end_in_src(tgt_df=tgt_df, src_df=df)

            # Step03: update df_tgt._scd_end_time from null to df_source._scd2_start_time
            rs_df = self._update_end_time_in_tgt(tgt_df=tgt_df, src_df=src_df)

            # Step04: combine 2 df together
            return rs_df.unionByName(src_df, allowMissingColumns=True)

        # NOTE: if target table doesn't exist or db_name and table name are not
        #   provided, choose created_at as {scd2_start_col}.
        return df.withColumns(
            {
                self.col_start_name: col(self.create_key),
                self.col_end_name: lit(None).cast("timestamp"),
            }
        )

    def _add_start_and_end_in_src(
        self,
        tgt_df: DataFrame,
        src_df: DataFrame,
    ) -> DataFrame:
        """Add thr `_scd2_start_time` and `_scd_end_time` columns to the source
        DataFrame.
        """
        from pyspark.sql import functions as f

        # NOTE: get existing id in target table and max updated_at value
        tgt_df_max: DataFrame = tgt_df.groupby(self.merge_key).agg(
            f.max(self.update_key).alias("_max_update_key")
        )
        src_df_merge = src_df.join(tgt_df_max, on=self.merge_key, how="left")

        # NOTE: Persist it before checking the wrong updated_at value to prevent
        #   recompute data.
        src_df_merge.persist()

        # NOTE: Check the wrong `updated_at` value from source
        #   - if target['_max_update_key'] > source[update_key]: it should not
        #       happen, we cannot get the past data from source.
        wrong_df: DataFrame = src_df_merge.filter(
            f.col("_max_update_key") > f.col(self.update_key)
        ).select(*(self.merge_key + [self.update_key, "_max_update_key"]))

        # NOTE: it's already persisted so should not take that much time to
        #   execute take(1)
        if not wrong_df.isEmpty():
            wrong_data: list[Row] = wrong_df.take(1)
            raise ValueError(
                f"There are wrong `{self.update_key}` from source. It's lower "
                f"than the existing value in the target table.",
                f"This is the first row of the wrong data -> {wrong_data[0]}",
            )

        # NOTE: if target['_max_update_key'] = source[update_key]: this case
        #   will happen when that rows already exist in the target because of
        #   rerunning the same job. So no need to reprocess and save it again.
        src_df_merge_filter = src_df_merge.filter(
            (tgt_df_max["_max_update_key"] < src_df[self.update_key])
            | (tgt_df_max["_max_update_key"].isNull())
        )

        if src_df_merge_filter.isEmpty():
            logger.info(
                "Every row in source df already existed in the target table. "
                "So you will get an empty dataframe result"
            )

        # NOTE: create scd2_start_col by checking join result
        check_merge_not_null: list[Column] = [
            tgt_df_max[key].isNotNull() for key in self.merge_key
        ]
        final_df: DataFrame = src_df_merge_filter.withColumns(
            {
                self.col_start_name: (
                    f.when(
                        *check_merge_not_null, src_df[self.update_key]
                    ).otherwise(src_df[self.create_key])
                ),
                self.col_end_name: f.lit(None).cast("timestamp"),
            }
        )

        # NOTE: remove merge key and _max_update_key that getting from join
        return final_df.select(
            src_df["*"], self.col_start_name, self.col_end_name
        )

    def _update_end_time_in_tgt(
        self,
        tgt_df: DataFrame,
        src_df: DataFrame,
    ) -> DataFrame:
        """Update tgt_df._scd_end_time from null to src_df._scd2_start_time."""
        merge_condition = [
            tgt_df[key] == src_df[key] for key in self.merge_key
        ] + [tgt_df[self.update_key] < src_df[self.update_key]]

        # NOTE: select only necessary using withColumn because we have
        #   duplicated column names
        final_df: DataFrame = tgt_df.join(
            src_df,
            on=merge_condition,
            how="inner",
        ).select(tgt_df["*"], src_df[self.col_start_name])

        # NOTE: update tgt_df[scd2_end_col] = src_df[scd2_start_col], then keep o
        #   nly target and new `_scd_end_time` column
        return final_df.withColumn(
            self.col_end_name, src_df[self.col_start_name]
        ).drop(src_df[self.col_start_name])


class ExplodeArrayColumn(BaseSparkTransform):
    """Explode Array Column Operation transform model."""

    op: Literal["explode_array"]
    explode_col: str
    is_explode_outer: bool = True
    is_return_position: bool = False
    position_prefix_name: str = "_index_pos"

    @field_validator("explode_col", "position_prefix_name", mode="after")
    def __validate_explode_col(cls, value: str) -> str:
        if "." in value:
            raise ValueError("Do not pass `.`, it supports only first level.")
        return value

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply to Explode Array Column.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.
        """
        from pyspark.sql import functions as f
        from pyspark.sql.functions import (
            explode,
            explode_outer,
            posexplode,
            posexplode_outer,
        )

        if not self.is_return_position:
            logger.info("Start Explode Array Column")
            if self.is_explode_outer:
                return df.withColumn(
                    self.explode_col, explode_outer(f.col(self.explode_col))
                )
            return df.withColumn(
                self.explode_col, explode(f.col(self.explode_col))
            )

        logger.info("Start Explode Array Column with Position.")
        pos_col_name: str = f"{self.position_prefix_name}_{self.explode_col}"
        if df.schema[self.explode_col].dataType.typeName() not in ("array",):
            raise ValueError("Support only ('array', ) data type")

        if pos_col_name in df.schema.fieldNames():
            raise ValueError(
                "Position column name is duplicated, please reconfigure "
                "`position_prefix_name` field."
            )
        selection: list[str] = [c for c in df.columns if c != self.explode_col]
        if self.is_explode_outer:
            return df.select(
                *selection,
                posexplode_outer(self.explode_col).alias(
                    pos_col_name, self.explode_col
                ),
            )
        return df.select(
            *selection,
            posexplode(self.explode_col).alias(pos_col_name, self.explode_col),
        )


class FlattenAllExceptArray(BaseSparkTransform):
    """Flatten all Columns except Array datatype Operator transform model."""

    op: Literal["flatten_all_columns_except_array"]

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply to Flatten all Columns except Array data type.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.

        Returns:
            DataFrame:
        """
        from pyspark.sql.functions import col

        transform_dict: dict[str, Column] = {}
        for c in extract_cols_without_array(schema=df.schema):
            flatten_col: str = "_".join(c.split("."))
            transform_dict[flatten_col] = col(c)

        logger.info("Start Flatten all columns except array")
        for k, v in transform_dict.items():
            logger.info(f"> Target col: {k}, from: {v}")
        return df.withColumns(transform_dict).select(
            *list(transform_dict.keys())
        )
