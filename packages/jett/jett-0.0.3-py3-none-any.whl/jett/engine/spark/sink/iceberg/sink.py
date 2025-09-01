from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field
from pydantic.functional_validators import field_validator, model_validator
from typing_extensions import Self

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, Row, SparkSession

from .....__types import DictData
from .....models import MetricSink
from .....utils import (
    clean_string,
    dt2str,
    format_bytes_humanreadable,
    regex_by_group,
    spark_env,
)
from ....__abc import BaseSink, Shape
from ...utils import (
    is_column_has_null,
    is_table_exist,
    is_timestamp_column,
    validate_col_allow_snake_case,
)
from .evolve import Evolver, EvolverModel
from .maintenance import TableMaintenance
from .utils import (
    SPARK_TEMP_VIEW_NAME,
    get_boundary_filter_condition,
    get_current_snapshot_id,
    get_hive_columns_from_df,
    get_iceberg_partition_transform_func,
    get_table_partition_columns,
)

logger = logging.getLogger("jett")


class Iceberg(BaseSink):
    """Iceberg Spark Sink model.

    :param merge_key: when mode is merge, merge key is the join key for upsert, merge key must be unique, and merge key can be many
    :param merge_sql_condition: when mode is merge, using sql condition for upsert
        it's required to use provided alias, where alias t is the target table and alias is source dataframe
        e.g. ON t.id = s.id AND t.sub_id = s.sub_id
             WHEN MATCHED AND s.op = 'delete' THEN DELETE
             WHEN MATCHED AND t.count IS NULL AND s.op = 'increment' THEN UPDATE SET t.count = 0
             WHEN MATCHED AND s.op = 'increment' THEN UPDATE SET t.count = t.count + 1
    :param partition_by: a list of columns to be partitioned, partitioning will respect the order of list
    :param table_property: a key-pair of Iceberg table property
    :param retention_days: a number of days that we will retain the data in the table
    :param retention_key: a timestamp column which will be used to filter data to be deleted
    :param keep_snapshot_days: a number of days that we will keep the snapshots,
        the snapshots that day older than param will be deleted
    :param keep_snapshot_at_least: a number of snapshots which will be retained after snapshot's expiration procedure
    :param schema_evolve_behavior: mode for table schema evolution, option is trust_source, merge, and trust_sink
    :param find_last_record_from_column: a timestamp column and the column must be first level column,
        if supply, the writer finds the maximum value of given column and put into the metric collector
        this computes after writer completes the write operation
    :param validate_column_snake_case: a boolean flag, if True, it validates that all columns in
        the DataFrame must be snake case
    :param allow_evolve_with_missing_columns: a boolean flag, if True, the workflow logic will apply table schema into
        given dataframe before writing to the target table
    :param allow_cast_safe_dtype: a boolean flag, if True, it allows to change data type of compatible columns
        (e.g. int (column in df) can be converted into double (column in table))
    """

    type: Literal["iceberg"]
    mode: Literal["append", "overwrite", "merge"] = Field(
        default="overwrite",
        description=(
            "A write mode that should be `append`, `overwrite`, or `merge` "
            "only."
        ),
    )
    database: str = Field(
        pattern=r"^[a-z0-9_]*$", description="A database name."
    )
    table_name: str = Field(
        pattern=r"^[a-z0-9_]*$", description="A table name."
    )
    table_property: dict | None = Field(default_factory=dict)
    retention_days: int | None = None
    retention_key: str | None = None
    keep_snapshot_days: int | None = 30
    keep_snapshot_at_least: int | None = 7
    find_last_record_from_column: str | None = None
    validate_column_snake_case: bool = True
    merge_key: list[str] | str | None = None
    merge_sql_condition: str | None = None

    partition_by: list[str] = Field(default_factory=list)
    schema_evolve_behavior: Literal["trust_source", "append", "trust_sink"]
    allow_evolve_with_missing_columns: bool = False
    allow_cast_safe_dtype: bool = False

    @field_validator("retention_days", mode="after")
    def __retention_period(cls, value: int | None) -> int | None:
        if value is not None and value < 1:
            raise ValueError("The `retention_days` should more than 0.")
        return value

    @model_validator(mode="after")
    def __necessary_fields(self) -> Self:
        """Validate necessary fields for this Iceberg Sink model."""
        if self.mode == "merge":
            if self.merge_key is None and self.merge_sql_condition is None:
                raise ValueError(
                    "merge mode requires merge_key or merge_sql_condition"
                )

            if (
                self.merge_key is not None
                and self.merge_sql_condition is not None
            ):
                raise ValueError(
                    "Please choose either merge_key or merge_sql_condition"
                )

        if self.retention_days is not None and self.retention_key is None:
            raise ValueError("Please input a timestamp column")

        if (
            self.schema_evolve_behavior != "append"
            and self.allow_evolve_with_missing_columns
        ):
            raise ValueError(
                "iceberg evolver `allow_evolve_with_missing_columns` option "
                "only use with schema_evolve_behavior `append`."
            )
        return self

    def validate_partition_exists(self, df: DataFrame) -> None:
        """Validate the partition column, it can be only first level column,
        not support struct

        Args:
            df (DataFrame): A Spark DataFrame.
        """
        if self.partition_by:
            first_columns_lv: list[str] = [
                c.name
                for c in df.schema
                if "struct" not in c.simpleString().split(":")[1]
            ]
            partition_cols: list[str] = []
            for p in self.partition_by:
                # NOTE: Start Prepare string value if it passes with bucket like
                #   `["bucket(2, _id)"]`.
                #   - Step: "bucket(2, _id)" -> "2, _id)"
                #   - Step: "2, _id)"        -> "2, _id"
                #   - Step: "2, _id"         -> " _id"
                #   - Step: " _id"           -> "_id"
                #
                _p: str = p.split("(")[-1]
                _p: str = _p.replace(")", "")
                _p: str = _p.split(",")[-1]
                _p: str = _p.strip()
                partition_cols.append(_p)

            for p in partition_cols:
                if p not in first_columns_lv:
                    raise ValueError(
                        f"Partition column {p} not found, partition column "
                        f"must be 1st level column only"
                    )

    def _extract_merge_key(self, df) -> list[str]:
        """Get merge key from component model."""
        merge_keys = None
        if self.merge_key is not None:
            merge_keys = (
                [self.merge_key]
                if isinstance(self.merge_key, str)
                else self.merge_key
            )
        elif self.merge_sql_condition is not None:
            on_clause = re.split(
                r"(?i)when",
                re.split(r"(?i)on", self.merge_sql_condition, maxsplit=1)[1],
                maxsplit=1,
            )[0].strip()
            merge_keys = re.findall(r"s\.(\w+)", on_clause)

        missing_keys = [key for key in merge_keys if key not in df.columns]
        if not merge_keys or missing_keys:
            raise ValueError(
                f"please check source dataframe, there are missing merge keys: {missing_keys}"
            )
        return merge_keys

    def _validate_duplicate_merge_key(self, df: DataFrame) -> None:
        """
        Validate that there are no duplicate values in the merge_key columns
        """
        if self.mode != "merge":
            return

        merge_keys = self._extract_merge_key(df=df)

        duplicate_df = df.groupBy(*merge_keys).count().filter("count > 1")
        if not duplicate_df.isEmpty():
            raise ValueError(
                f"Duplicate values found for merge keys: {merge_keys}"
            )

    def _get_table_property(self) -> str:
        """
        get and update default table property
        """
        table_property = self._default_table_property
        if len(self.table_property) > 0:
            for k, v in self.table_property.items():
                table_property[k] = v

        table_property = [f"'{k}'='{v}'" for k, v in table_property.items()]
        table_property = ",\n".join(table_property)
        return table_property

    def get_partition_ddl(self) -> str:
        """Get partition by clause."""
        if self.partition_by:
            return f"PARTITIONED BY ({', '.join(self.partition_by)})"
        return ""

    def get_table_ddl(self, df: DataFrame) -> str:
        """
        get iceberg table ddl
        """
        columns = get_hive_columns_from_df(df=df)
        table_property = self._get_table_property()
        partition_by = self.get_partition_ddl()
        ddl = self._create_table_stmt.format(
            hive_db=self.database,
            table_name=self.table_name,
            columns=columns,
            partition_by=partition_by,
            properties=table_property,
        )
        ddl = clean_string(text=ddl)
        return ddl

    def _create_database(self, spark: SparkSession) -> None:
        """
        create database if not exist, for local environment only
        aws env and iu env must already create the Hive DB
        """
        if spark_env("ENV") == "local":
            if not spark.catalog.databaseExists(dbName=self.database):
                # NOTE: no need to define location since it's already defined
                #   in spark-warehouse.
                ddl: str = f"CREATE DATABASE {self.database}"
                logger.info("database does not exists, create a database")
                logger.info("execute sparksql: %s", ddl)
                spark.sql(ddl)
        else:
            if not spark.catalog.databaseExists(dbName=self.database):
                raise RuntimeError(
                    "please create database in your env (aws / iu) before write a table"
                )

    def _create_table(
        self, df: DataFrame, spark: SparkSession, metric: MetricSink
    ) -> None:
        """
        create iceberg table if not exist
        """
        if not is_table_exist(
            spark=spark,
            database=self.database,
            table_name=self.table_name,
        ):
            ddl = self.get_table_ddl(df=df)
            logger.info("table does not exist, create a new iceberg table")
            logger.info(f"execute sparksql: {ddl}")
            spark.sql(ddl)
            self._is_table_created = True

            # NOTE: set metric sink of table operation when table is created.
            operations = []
            for schema in df.schema.fields:
                _s = schema.simpleString().split(":", maxsplit=1)
                operations.append(
                    {
                        "name": _s[0],
                        "data_type": _s[1],
                    }
                )
            metric.add(
                key="table_operation_create_table_columns",
                value=operations,
            )
        else:
            logger.info("table exists")
            self._is_table_created = False

    def _get_append_statement(self) -> str:
        """
        get SparkSQL insert into statement
        """
        sql = f"INSERT INTO {self.database}.{self.table_name} SELECT * FROM {SPARK_TEMP_VIEW_NAME}"
        sql = clean_string(text=sql)
        return sql

    def _get_overwrite_statement(self, spark: SparkSession) -> str:
        """
        get SparkSQL insert overwrite statement
        """
        spark.sql("SET spark.sql.sources.partitionOverwriteMode=dynamic")
        sql = f"INSERT OVERWRITE {self.database}.{self.table_name} SELECT * FROM {SPARK_TEMP_VIEW_NAME}"
        sql = clean_string(text=sql)
        return sql

    def _get_merge_table_filter_condition(
        self, df: DataFrame, spark: SparkSession
    ) -> str:
        """
        get filter condition using in MERGE operation
        help reducing data scanning
        """
        allow_partition_transform_func = [
            "year",
            "month",
            "day",
            "hour",
        ]

        table_filter = None
        partition_spec = get_table_partition_columns(
            spark=spark,
            db_name=self.database,
            table_name=self.table_name,
        )
        if len(partition_spec) > 0:
            # assume that 1st partition column must be a timestamp column, if not it cannot apply filter
            first_partition_spec = partition_spec[0]
            transform_func = get_iceberg_partition_transform_func(
                partition_spec=first_partition_spec
            )
            if transform_func in allow_partition_transform_func:
                partition_col = regex_by_group(
                    text=first_partition_spec,
                    regex=r"(?<=\()[^)]+(?=\))",
                    n=0,
                )  # get everything inside ()

                logger.info(
                    "found 1st partition column that is a timestamp column: %s",
                    first_partition_spec,
                )
                logger.info("get timestamp filter for merge operation")
                sql = f"""
                    SELECT MIN({partition_col}) AS min_val, MAX({partition_col}) AS max_val
                    FROM {SPARK_TEMP_VIEW_NAME} WHERE {partition_col} IS NOT NULL
                """
                data_row = spark.sql(sql).collect()[0]
                logger.info("min value: %s", data_row.min_val)
                logger.info("max value: %s", data_row.max_val)

                if data_row.min_val is None or data_row.max_val is None:
                    logger.info(
                        "There are all None in partition column `%s`. So we will filter target table in null partition only ",
                        partition_col,
                    )
                    table_filter = f"t.{partition_col} IS NULL"
                    return table_filter

                min_val, max_val = get_boundary_filter_condition(
                    transform_func=transform_func,
                    start=data_row.min_val,
                    end=data_row.max_val,
                )

                table_filter = f'(t.{partition_col} >= "{min_val}" AND t.{partition_col} < "{max_val}")'

                # check that df contains null or not
                is_col_has_null = is_column_has_null(
                    df=df, column=partition_col
                )
                if is_col_has_null:
                    table_filter = (
                        f"({table_filter} OR t.{partition_col} IS NULL)"
                    )

        return table_filter

    def _get_merge_condition(self, df: DataFrame, spark: SparkSession) -> str:
        """
        get merge condition
        """
        merge_condition = self.merge_sql_condition
        if self.merge_key is not None:
            _merge_key = self.merge_key
            if isinstance(self.merge_key, str):
                _merge_key = [self.merge_key]
            merge_clauses = [f"t.{k} = s.{k}" for k in _merge_key]
            if not self._is_table_created:
                table_filter = self._get_merge_table_filter_condition(
                    df, spark=spark
                )
                if table_filter is not None:
                    merge_clauses = merge_clauses + [table_filter]
            on_condition = " AND ".join(merge_clauses)
            merge_condition = f"""
            ON {on_condition}
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
            """
        merge_condition = clean_string(merge_condition)
        return merge_condition

    def _get_merge_statement(self, df: DataFrame, spark: SparkSession) -> str:
        """
        get SparkSQL merge into statement
        """
        merge_condition = self._get_merge_condition(df=df, spark=spark)
        sql = f"""
        MERGE INTO {self.database}.{self.table_name} AS t
        USING (SELECT * FROM {SPARK_TEMP_VIEW_NAME}) AS s
        {merge_condition}
        """
        sql = clean_string(sql)
        return sql

    def _get_write_sql_statement(
        self, df: DataFrame, spark: SparkSession
    ) -> str:
        sql = None
        logger.info("iceberg write mode: %s", self.mode)
        match self.mode:
            case "append":
                sql = self._get_append_statement()
            case "overwrite":
                sql = self._get_overwrite_statement(spark=spark)
            case "merge":
                sql = self._get_merge_statement(df, spark=spark)
        return sql

    def _get_write_statistics(self, spark: SparkSession) -> dict:
        """Get write statistics of last table write operation."""
        snapshot_id: str = get_current_snapshot_id(
            spark=spark, database=self.database, table_name=self.table_name
        )
        raw_stats: Row = spark.sql(
            f"SELECT * FROM {self.database}.{self.table_name}.snapshots "
            f"WHERE snapshot_id = '{snapshot_id}'"
        ).collect()[0]
        added_file_size = raw_stats.summary.get("added-files-size", 0)
        stats = {
            "written_rows": raw_stats.summary.get("added-records", 0),
            "written_bytes": added_file_size,
            "written_bytes_formatted": (
                format_bytes_humanreadable(int(added_file_size))
                if added_file_size is not None
                else None
            ),
            "affected_partitions": raw_stats.summary.get(
                "changed-partition-count", 0
            ),
        }
        return stats

    def _find_last_record_from_column(
        self,
        spark: SparkSession,
        metric: MetricSink,
    ) -> None:
        """Compute last record of given input and set the metric."""
        if self.find_last_record_from_column is not None:
            table_schema = spark.sql(
                f"SELECT * FROM {self.database}.{self.table_name} LIMIT 0"
            ).schema
            is_timestamp_col = is_timestamp_column(
                column_name=self.find_last_record_from_column,
                schema=table_schema,
            )
            if not is_timestamp_col:
                raise ValueError(
                    f"{self.find_last_record_from_column} is not a timestamp "
                    f"column",
                )

            logger.info(
                "find last record from column: %s",
                self.find_last_record_from_column,
            )
            find_last = f"""
                SELECT MAX(
                    readable_metrics.{self.find_last_record_from_column}.upper_bound
                )
                FROM {self.database}.{self.table_name}.files
            """
            find_last = clean_string(find_last)
            logger.info(find_last)
            last_record = spark.sql(find_last).first()[0]
            last_record = dt2str(last_record, sep=" ", timespec="microseconds")

            logger.info("last record: %s", last_record)
            metric.add("latest_record_update", last_record)
            metric.add(
                "latest_record_update_from_column",
                self.find_last_record_from_column,
            )

    def _apply_table_schema_to_dataframe(
        self, df: DataFrame, spark: SparkSession
    ) -> DataFrame:
        if self.allow_evolve_with_missing_columns:
            current_table_schema = spark.sql(
                f"SELECT * FROM {self.database}.{self.table_name} LIMIT 0"
            ).schema
            if df.schema != current_table_schema:
                logger.info("apply table schema to dataframe")
                df = df.to(current_table_schema)

        return df

    def save(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricSink,
        **kwargs,
    ) -> Any:
        """Save the result data to the Iceberg table.

        Args:
            df (DataFrame): A Spark DataFrame.
            engine (DictData):
            metric (MetricSink):
        """
        logger.info("Sink - Start sink to Iceberg.")
        spark: SparkSession = engine["spark"]

        if df.isEmpty():
            logger.warning("Sink - Found empty dataframe, skip write")
            metric.add("affected_partitions", 0)
            return df, Shape(rows=0, columns=0)

        logger.info("Sink - Validate table spec and dataframe")
        if self.validate_column_snake_case:
            validate_col_allow_snake_case(schema=df.schema)
        self.validate_partition_exists(df=df)

        logger.info(f"> database name: {self.database}")
        logger.info(f"> table name: {self.table_name}")

        logger.info("Start Iceberg Table Evolve ...")
        evolve_model = EvolverModel.model_validate(self, from_attributes=True)
        evolver = Evolver(model=evolve_model, df=df, spark=spark)

        logger.info("start table maintenance ...")
        maintain = TableMaintenance.model_validate(self, from_attributes=True)
        maintain.validate_retention_key(df)

        # start Iceberg write operation
        logger.info("write df to iceberg table")
        self._create_database(spark=spark)
        self._create_table(df, spark=spark, metric=metric)

        evolver.evolve_schema()
        evolver.evolve_partition()
        df = evolver.df

        metric.add("alter_history", evolver.list_sql_alter)
        alter_list, add_list, drop_list = evolver.get_simple_detail_changes()
        metric.add("table_operation_alter_columns", alter_list)
        metric.add("table_operation_add_columns", add_list)
        metric.add("table_operation_drop_columns", drop_list)

        df = self._apply_table_schema_to_dataframe(df, spark=spark)

        self._validate_duplicate_merge_key(df=df)
        df.createOrReplaceTempView(SPARK_TEMP_VIEW_NAME)
        sql = self._get_write_sql_statement(df=df, spark=spark)
        logger.info("start writing data into table")
        logger.info(f"Sink - Execute sparksql: {sql}")
        spark.sql(sql)
        logger.info("wrote successfully")

        stats = self._get_write_statistics(spark=spark)
        logger.info(f"> Written rows: {stats['written_rows']}")
        logger.info(
            f"> Written bytes: {stats['written_bytes']} "
            f"({stats['written_bytes_formatted']})"
        )
        logger.info(
            f"> Written Affected partitions: {stats['affected_partitions']}"
        )
        metric.add("affected_partitions", int(stats.get("affected_partitions")))

        maintain.retain_data(spark=spark)
        maintain.expire_snapshot(spark=spark)

        # NOTE: Write operation already completed
        self._find_last_record_from_column(spark=spark, metric=metric)
        return (
            df,
            Shape(rows=stats.get("written_rows"), columns=len(df.columns)),
        )

    def outlet(self) -> tuple[str, str]:
        return "iceberg", self.dest()

    def dest(self) -> str:
        return f"{self.table_name}"
