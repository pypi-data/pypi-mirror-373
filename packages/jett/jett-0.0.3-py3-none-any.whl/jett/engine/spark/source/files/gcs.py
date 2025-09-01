from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING, Literal

from pydantic import Field

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.connect.session import SparkSession as SparkRemoteSession

    AnySparkSession = SparkSession | SparkRemoteSession

from .....__types import DictData
from .....models import BasicFilter, Shape
from .....utils import bool2str
from ....__abc import BaseSource
from ...utils import is_remote_session

logger = logging.getLogger("jett")


class BaseGCSFile(BaseSource, ABC):
    type: Literal["gcs"]
    path: str
    file_format: str
    auth_type: str = "SERVICE_ACCOUNT_JSON_KEYFILE"
    auth_service_account_json_keyfile: str | None = None
    impl: str = "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
    sample_records: int | None = None
    filter: list[BasicFilter] = Field(default_factory=list)

    def set_gcs_connection(self, spark: AnySparkSession) -> None:
        """Set gcs connection in SparkContext."""
        logger.info("set fs.gs.impl=%s", self.impl)
        logger.info("set fs.gs.auth.type=%s", self.auth_type)
        logger.info(
            "set fs.gs.auth.service.account.json.keyfile=%s",
            self.auth_service_account_json_keyfile,
        )

        hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
        hadoop_conf.set("fs.gs.impl", self.impl)
        hadoop_conf.set("fs.gs.auth.type", self.auth_type)

        # TODO
        # need to refactor this flow if we gonna support more auth type
        hadoop_conf.set(
            "fs.gs.auth.service.account.json.keyfile",
            self.auth_service_account_json_keyfile,
        )

    def inlet(self) -> tuple[str, str]:
        return "gcs", self.path


class GCSCSVFile(BaseGCSFile):
    file_format: Literal["csv"]
    delimiter: str = "|"
    header: bool = Field(default=True)

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        """Apply GCS CSV Loading process with the Spark session object."""
        spark: SparkSession = engine["spark"]
        if is_remote_session(spark):
            raise RuntimeError(
                f"Source: {self.type} does not support Spark Connect Session"
            )
        logger.info(f"🚰 Source - Start Load GCS: {self.path}")
        self.set_gcs_connection(spark=spark)
        reader = spark.read.format(self.file_format)

        df: DataFrame = (
            reader.option("header", bool2str(self.header))
            .option("delimiter", self.delimiter)
            .option("inferSchema", "true")
            .load(self.path)
        )

        if self.filter:
            df = df.filter(" and ".join(f.get_str_cond() for f in self.filter))

        if self.sample_records:
            logger.info(f"🚰 Source - apply limit: {self.sample_records}")
            df = df.limit(self.sample_records)

        rows: int = df.count()
        shape: tuple[int, int] = (rows, len(df.columns))
        return df, Shape.from_tuple(shape)


class GCSJsonFile(BaseGCSFile):
    file_format: Literal["json"]
    multiline: bool = False

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        spark: SparkSession = engine["spark"]
        if is_remote_session(spark):
            raise RuntimeError(
                f"Source: {self.type} does not support Spark Connect Session"
            )
        logger.info(f"🚰 Source - Start Load GCS: {self.path}")
        self.set_gcs_connection(spark=spark)
        reader = spark.read.format(self.file_format)

        df: DataFrame = (
            reader.option("inferSchema", "true")
            .option("multiline", bool2str(self.multiline))
            .load(self.path)
        )

        if self.filter:
            df = df.filter(" and ".join(f.get_str_cond() for f in self.filter))

        if self.sample_records:
            logger.info(f"🚰 Source - apply limit: {self.sample_records}")
            df = df.limit(self.sample_records)

        rows: int = df.count()
        shape: tuple[int, int] = (rows, len(df.columns))
        return df, Shape.from_tuple(shape)
