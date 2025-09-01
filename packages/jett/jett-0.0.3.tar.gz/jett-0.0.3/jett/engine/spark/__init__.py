from __future__ import annotations

import logging
import subprocess
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from pydantic import Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self

from ...__about__ import __version__
from ...__types import DictData, PrimitiveType
from ...models import (
    ColDetail,
    Context,
    MetricEngine,
    MetricOperatorTransform,
    MetricTransform,
    Result,
)
from ...utils import exec_command, regex_by_group, sort_non_sensitive_str
from ..__abc import BaseEngine
from .schema_change import (
    clean_col_except_item_from_extract_array,
)
from .sink import Sink
from .source import Source
from .temp_storage import TempStorage
from .transform import Transform
from .utils import (
    add_spark_cmd,
    clean_tz_for_extra_java_options,
    extract_cols_without_array,
    extract_spark_conf_keys,
    is_remote_session,
    schema2dict,
    yarn_fetch_log,
    yarn_kill,
)

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, SparkSession
    from pyspark.sql.connect.session import DataFrame as DataFrameRemote
    from pyspark.sql.connect.session import SparkSession as SparkRemoteSession
    from pyspark.sql.types import StructType

    PairCol = tuple[Column, str]
    AnyDataFrame = DataFrame | DataFrameRemote
    AnySparkSession = SparkSession | SparkRemoteSession

logger = logging.getLogger("jett")


class EngineContext(TypedDict):
    """Engine Context dict typed for Spark engine execution."""

    spark: SparkSession
    engine: Spark
    temp_storage: dict[str, Any]


class Spark(BaseEngine):
    """Spark Engine model. This engine will execute Pyspark via connect on the
    current context.
    """

    type: Literal["spark"] = Field(description="A type of spark engine.")
    app_name: str | None = Field(
        default=None, description="An application name."
    )
    enable_collect_result: bool = Field(
        default=False,
        description=(
            "A flag that use for enable collect data from LazyFrame after the "
            "execution done."
        ),
    )
    source: Source = Field(description="A source model.")
    sink: Sink = Field(description="A sink model.")
    transforms: list[Transform] = Field(
        default_factory=list,
        description="A list of transform model.",
    )
    master: str | None = None
    remote: str | None = None
    deploy_mode: Literal["cluster"] = "cluster"
    jars: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    timezone: str = "UTC"
    driver_memory: str = "1G"
    driver_cores: int = 1
    executor_memory: str = "2G"
    executor_cores: int = 1
    num_executors: int = 2
    max_executors: int = 5
    show_all_spark_submit_log: bool = False
    enable_hive_support: bool = False
    conf: dict[str, PrimitiveType | None] = Field(default_factory=dict)

    def _validate_master_and_remote(self) -> None:
        """Validate master and remote fields.

        Raises:
            ValueError: If the master and remote fields does not set, or it set
                together.
        """
        if (self.master and self.remote) or (
            self.master is None and self.remote is None
        ):
            raise ValueError(
                "please choose either master or remote to be specify."
            )

    @model_validator(mode="after")
    def validate_after(self) -> Self:
        """Validate Spark engine after mode."""
        self._validate_master_and_remote()
        return self

    def session(self, context: Context, **kwargs) -> SparkSession:
        """Create Spark Session with this model engine configuration data.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.

        Returns:
            SparkSession: return spark session.
        """
        from pyspark.sql import SparkSession

        _ = kwargs
        builder = SparkSession.builder
        if self.master:
            builder = builder.master(self.master)
        else:
            builder = builder.remote(self.remote)

        builder = builder.appName(self.app_name or self.name).config(
            map={
                "spark.driver.memory": "2G",
                "spark.driver.cores": 1,
            }
            | self.conf
        )
        if self.jars:
            builder = builder.config("spark.jars", ",".join(self.jars))

        if self.files:
            builder = builder.config("spark.files", ",".join(self.files))

        if self.enable_hive_support:
            builder = builder.enableHiveSupport()

        spark: SparkSession = builder.getOrCreate()

        logger.info(f"Spark Session: {spark}")

        if is_remote_session(spark):
            context["metric_engine"].app_id = spark.sparkContext.applicationId
        return spark

    def set_engine_context(self, context: Context, **kwargs) -> EngineContext:
        """Create Spark Engine Context data for passing to the execute method.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.

        Returns:
            DictData: A mapping of necessary data for Spark execution.
        """
        return {
            "spark": self.session(context, **kwargs),
            "engine": self,
            "temp_storage": {},
        }

    def execute(
        self, context: Context, engine: DictData, metric: MetricEngine
    ) -> DataFrame:
        """Execute Spark engine method. This method do procedure process to load
        data from source and save it to the sink model.

            This method start process with 3 steps:
                1. Handle source load method
                2. Handle apply operator transform
                3. Handle sink save method

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricEngine): A metric engine that was set from handler
                step for passing custom metric data.

        Returns:
            DataFrame: A result DataFrame API.
        """
        logger.info("🏗️ Start execute with Spark engine.")
        # NOTE: Start run source handler.
        df: DataFrame = self.source.handle_load(context, engine=engine)

        # NOTE: Start run transform handler.
        df: DataFrame = self.handle_apply(df, context, engine=engine)

        # NOTE: Start run sink handler.
        self.sink.handle_save(df, context, engine=engine)
        return df

    def set_result(self, df: DataFrame, context: DictData) -> Result:
        """Set the Result object for this Spark engine.

        Args:
            df (DataFrame): A Spark DataFrame.
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.

        Returns:
            Result: A result object that catch schema and sample data from the
            execution result DataFrame.
        """
        if self.enable_collect_result:
            logger.warning(
                "⚠️ If you collect results from the DataFrame, it will fetch all "
                "records in the DataFrame. This is not ideal for any ETL "
                "pipeline with large data sizes. Please use it only for "
                "testing purposes or with smaller datasets."
            )
        schema: StructType = df.schema
        return Result(
            data=df.collect() if self.enable_collect_result else [],
            columns=[
                ColDetail(name=f.name, dtype=f.dataType.simpleString())
                for f in schema
            ],
            schema_dict=df.schema.jsonValue(),
        )

    def post_execute(
        self,
        context: Context,
        *,
        engine: DictData,
        exception: Exception | None = None,
        **kwargs,
    ) -> None:
        """Post-execute Spark engine. This method use to clear a temp storage
        after execute all layer of execution method.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            exception (Exception, default None): An exception class that raise
                from execution method. It will be None value if it completes
                without raise any exception.
        """
        logger.info("🎢 Start Post Spark Execution ...")
        tmp_st: dict[str, TempStorage | None] = engine["temp_storage"]

        # NOTE: Clear source temp storage.
        temp_source: TempStorage | None = tmp_st.get("source")
        if temp_source is not None and temp_source.is_written:
            temp_source.teardown()

        # NOTE: Clear sink temp storage.
        temp_sink: TempStorage | None = tmp_st.get("sink")
        if temp_sink is not None and temp_sink.is_written:
            temp_sink.teardown()

        engine["spark"].stop()

    def apply(
        self,
        df: DataFrame,
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> DataFrame:
        """Apply Spark engine transformation to the source. This method will
        apply all operators by priority.

            The Spark engine apply the split sub-apply on transform operators
        to 3 layers of priority:
            1. pre layer: An ordering transform before group transform
            2. group layer: A group transform
            3. post layer: A ordering transform after group transform

        Args:
            df (DataFrame): A Spark DataFrame.
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricTransform): A metric transform that was set from
                handler step for passing custom metric data.
        """
        spark: SparkSession = engine["spark"]
        priority: list[Transform] = []
        groups: list[Transform] = []
        fallback: list[Transform] = []

        logger.debug("⚙️ Transform - Prepare transform analyzer ...")
        for t in self.transforms:
            if t.priority == "pre":
                priority.append(t)
            elif t.priority == "group":
                groups.append(t)
            else:
                fallback.append(t)

        logger.info(f"⚙️ Priority transform count: {len(priority)}")
        for t in priority:
            logger.info(f"Start priority operator: {t.op!r}")
            df: DataFrame = t.handle_apply(
                df,
                context=context,
                engine=engine,
                spark=spark,
            )

        logger.info(f"⚙️ Group transform count: {len(groups)}")
        if groups:
            maps: dict[str, Column] = {}
            for t in groups:
                # NOTE: Generate sub transform for apply group transform.
                maps.update(
                    t.handle_apply_group(
                        df, context, engine=engine, spark=spark
                    )
                )

            if len(maps) > 0:
                for k, v in maps.items():
                    logger.info(f"... target col: {k}, from: {v}")
                pre_schema: StructType = df.schema
                df: DataFrame = df.withColumns(maps)
                self.sync_schema_group(
                    pre_schema, df.schema, context=context, spark=spark
                )

        logger.info(f"⚙️ Fallback transform count: {len(fallback)}")
        for t in fallback:
            logger.info(f"Start fallback operator: {t.op!r}")
            df: DataFrame = t.handle_apply(
                df,
                context,
                engine=engine,
                spark=spark,
            )

        return df

    @staticmethod
    def sync_schema_group(
        pre: StructType,
        post: StructType,
        *,
        context: Context,
        spark: SparkSession | None = None,
    ) -> None:
        """Update pre- and post-schema metrics data for any transform that apply
        to the source DataFrame API until it save to the sink.

        Args:
            pre (StructType): A pre-transform StructType object.
            post (StructType): A post-transform StructType object.
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            spark (SparkSession, default None): A Spark session.
        """
        pre_schema = spark.createDataFrame(data=[], schema=pre).schema
        post_schema = spark.createDataFrame(data=[], schema=post).schema
        pre_no_array = sort_non_sensitive_str(
            extract_cols_without_array(schema=pre_schema)
        )
        post_no_array = sort_non_sensitive_str(
            extract_cols_without_array(schema=post_schema)
        )
        metric: MetricOperatorTransform = context["metric_group_transform"]

        # NOTE: Start update the pre- and post-schema metric.
        metric.transform_pre = {
            "schema": schema2dict(pre, sorted_by_name=True),
            "schema_no_array": pre_no_array,
        }
        metric.transform_post = {
            "schema": schema2dict(post, sorted_by_name=True),
            "schema_no_array": post_no_array,
        }
        context["metric_operator"].append(metric)


class SparkSubmit(Spark):
    """Spark Submit Engine model."""

    type: Literal["spark-submit"] = Field(
        description="A type of spark submit engine."
    )
    entrypoint: str = Field(
        description="An entrypoint of the Spark submit command.",
    )
    archives: list[str] = Field(default_factory=list)
    py_files: list[str] = Field(default_factory=list)
    env_var: dict[str, str] = Field(default_factory=dict)
    queue: str | None = None
    keytab_path: str | None = None
    keytab_principal: str | None = None
    yarn_app_id: str | None = Field(
        default=None,
        description="A YARN application ID after submit the Spark application.",
    )

    @model_validator(mode="after")
    def validate_after(self) -> Self:
        """Inherit after validation from Spark engine model for checking master
        field value that allow to use this Spark submit engine.
        """
        self._validate_master_and_remote()
        if self.master and self.master.startswith("local"):
            raise ValueError("Spark Submit does not support for local master.")
        return self

    def get_cmd(self) -> list[str]:
        """Generate Spark submit commands from all model field."""
        cmd: list[str] = ["spark-submit"]
        add_spark_cmd(cmd, "master", self.master)
        add_spark_cmd(cmd, "name", self.app_name)
        add_spark_cmd(cmd, "deploy-mode", self.deploy_mode)
        add_spark_cmd(cmd, "archives", self.archives)
        add_spark_cmd(cmd, "files", self.files)
        add_spark_cmd(cmd, "py-files", self.py_files)
        add_spark_cmd(cmd, "jars", self.jars)
        add_spark_cmd(cmd, "driver-memory", self.driver_memory)
        add_spark_cmd(cmd, "driver-cores", self.driver_cores)
        add_spark_cmd(cmd, "executor-memory", self.executor_memory)
        add_spark_cmd(cmd, "executor-cores", self.executor_cores)
        add_spark_cmd(cmd, "num-executors", self.num_executors)
        add_spark_cmd(cmd, "keytab", self.keytab_path)
        add_spark_cmd(cmd, "principal", self.keytab_principal)
        add_spark_cmd(cmd, "queue", self.queue)

        if self.enable_hive_support:
            cmd.extend(["--conf", '"spark.sql.catalogImplementation=hive"'])

        if self.max_executors:
            cmd.extend(
                [
                    '--conf "spark.dynamicAllocation.enabled=True"',
                    f'--conf "spark.dynamicAllocation.maxExecutors={str(self.max_executors)}"',
                ]
            )

        # NOTE: Set timezone
        driver_extra_ops = clean_tz_for_extra_java_options(
            option=self.conf.get("spark.driver.extraJavaOptions", ""),
            tz=self.timezone,
        )
        executor_extra_ops = clean_tz_for_extra_java_options(
            option=self.conf.get("spark.executor.extraJavaOptions", ""),
            tz=self.timezone,
        )
        cmd.extend(
            [
                "--conf",
                f'"spark.sql.session.timeZone={self.timezone}"',
                "--conf",
                f'"spark.driver.extraJavaOptions={driver_extra_ops}"',
                "--conf",
                f'"spark.executor.extraJavaOptions={executor_extra_ops}"',
            ]
        )

        if self.conf:
            exist_spark_conf: list[str] = extract_spark_conf_keys(cmd=cmd)
            cmd.extend(
                [
                    f'--conf "{k}={self.conf[k]}"'
                    for k in self.conf
                    if k not in exist_spark_conf
                ]
            )

        cmd.extend(["--conf", f'"spark.jett.version={__version__}"'])

        if self.master == "yarn" and self.deploy_mode == "cluster":
            for k, v in self.env_var.items():
                cmd.extend(["--conf", f'"spark.yarn.appMasterEnv.{k}={v}"'])

        cmd.append(self.entrypoint)
        return cmd

    def iter_submit_log(self, logs: Iterator[str]) -> None:
        """Logging spark submit log and grep YARN application ID.

        Args:
            logs (Iterator[str]): A yield of log statement.
        """
        already_log_yarn_url: bool = False
        states: list[str] = []
        for log in logs:
            log = log.strip()
            if self.show_all_spark_submit_log:
                logger.info(log)
            else:
                state: str = regex_by_group(log, regex=r"state:\s+(.+?)\)", n=1)
                if state not in states and state != "":
                    logger.info("application state: %s", state)
                    states.append(state)

            if self.master != "yarn" or self.deploy_mode != "cluster":
                continue

            app_id: str = regex_by_group(log, regex=r"application[0-9_]+")
            if app_id != "":
                self.yarn_app_id = app_id

            if self.show_all_spark_submit_log:
                continue

            if "tracking URL:" in log:
                _yarn_url: str = log.replace("tracking URL:", "").strip()
                if not already_log_yarn_url:
                    logger.info(f"YARN app id: {self.yarn_app_id}")
                    logger.info(f"YARN app tracking url: {_yarn_url}")
                    already_log_yarn_url = True

    def submit(self, context: Context) -> None:
        """Submit Spark application to YARN.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
        """
        submit_cmd: list[str] = self.get_cmd()
        logger.info(f"Spark Submit Command:\n{submit_cmd}")

        proc: subprocess.Popen = exec_command(" ".join(submit_cmd))
        self.iter_submit_log(iter(proc.stdout.readline, ""))
        return_code: int = proc.wait()
        if return_code != 0:
            # NOTE: kill app if YARN application in cluster mode
            if self.master == "yarn" and self.deploy_mode == "cluster":
                yarn_kill(app_id=self.yarn_app_id)
                yarn_fetch_log(
                    application_id=self.yarn_app_id, log_file="stdout,stderr"
                )
            raise RuntimeError(
                f"Failed to execute spark application, stderr: "
                f"{str(proc.stderr)}"
            )
        if self.master == "yarn" and self.deploy_mode == "cluster":
            yarn_fetch_log(application_id=self.yarn_app_id, log_file="stdout")

        context.update(
            {
                "metric_engine": MetricEngine(
                    app_id=self.yarn_app_id or self.app_name,
                )
            }
        )

    def apply(
        self,
        df: DataFrame,
        context: Context,
        *,
        engine: DictData,
        **kwargs,
    ) -> DataFrame:
        """Apply Spark engine transformation to the source. This method will
        apply all operators by priority.

            This engine does not allow to use apply method.
        """
        raise NotImplementedError(
            "Spark Submit Engine does not support apply transform."
        )

    def execute(
        self, context: Context, engine: DictData, metric: MetricEngine
    ) -> DataFrame:
        logger.info("Start execute with Spark Submit engine.")
        raise NotImplementedError(
            "Spark Submit Engine does not support direct execute yet."
        )
