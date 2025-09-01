from __future__ import annotations

import logging
import os
from abc import ABC
from typing import TYPE_CHECKING, Literal

from pydantic import Field, SecretStr
from pydantic.functional_validators import model_validator

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

from .....__types import DictData
from .....models import BasicFilter, Shape
from .....utils import bool2str
from ....__abc import BaseSource
from ...utils import is_remote_session

logger = logging.getLogger("jett")


class BaseS3File(BaseSource, ABC):
    """AWS S3 CSV file data source."""

    type: Literal["s3", "vos"]
    path: str
    file_format: str
    access_key: SecretStr | None = None
    secret_key: SecretStr | None = None
    session_token: SecretStr | None = None
    s3_endpoint: str
    s3_region: str | None = None
    s3_path_style: bool | None = True
    impl: str = "org.apache.hadoop.fs.s3a.S3AFileSystem"
    s3_credentials_provider: str = (
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
    )
    filter: list[BasicFilter] = Field(default_factory=list)

    @model_validator(mode="after")
    def __check_credential(self):
        """validate credential."""
        _access_key = os.getenv("AWS_ACCESS_KEY_ID", self.access_key)
        _secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", self.secret_key)
        _session_token = os.getenv("AWS_SESSION_TOKEN", self.session_token)

        if self.s3_credentials_provider in (
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
            "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider",
        ):
            if _access_key is None or _secret_key is None:
                raise ValueError(
                    "please supply access_key (env: AWS_ACCESS_KEY_ID) and "
                    "secret_key (env: AWS_SECRET_ACCESS_KEY)"
                )

            if (
                self.s3_credentials_provider
                == "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider"
            ):
                if _session_token is None:
                    raise ValueError(
                        "please supply session_token (AWS_SESSION_TOKEN)"
                    )

        return self

    def set_s3_connection(self, spark: SparkSession) -> None:
        """Set s3 connection in SparkContext.

        Args:
            spark (SparkSession): The current spark session object that will use
                to create a DataFrame Reader object.
        """
        logger.info("set fs.s3a.impl=%s", self.impl)
        logger.info("set fs.s3a.endpoint=%s", self.s3_endpoint)
        logger.info("set fs.s3a.path.style.access=true")
        logger.info(
            "set fs.s3a.aws.credentials.provider=%s",
            self.s3_credentials_provider,
        )

        hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
        hadoop_conf.set("fs.s3a.impl", self.impl)
        hadoop_conf.set("fs.s3a.endpoint", self.s3_endpoint)
        if self.s3_path_style:
            hadoop_conf.set("fs.s3a.path.style.access", "true")
        hadoop_conf.set(
            "fs.s3a.aws.credentials.provider",
            self.s3_credentials_provider,
        )

        if self.access_key is not None:
            hadoop_conf.set(
                "fs.s3a.access.key",
                self.access_key.get_secret_value(),
            )
            hadoop_conf.set(
                "fs.s3a.secret.key",
                self.secret_key.get_secret_value(),
            )

        if self.session_token is not None:
            hadoop_conf.set(
                "fs.s3a.session.token",
                self.session_token.get_secret_value(),
            )

        if self.s3_region is not None:
            hadoop_conf.set("fs.s3a.endpoint.region", self.s3_region)

    def inlet(self) -> tuple[str, str]:
        return "s3", self.path


class S3CSVFile(BaseS3File):
    file_format: Literal["csv"]
    delimiter: str = "|"
    header: bool = Field(default=True)

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        """Apply S3 CSV Loading process with the Spark session object."""
        spark: SparkSession = engine["spark"]
        if is_remote_session(spark):
            raise RuntimeError(
                f"Source: {self.type} does not support Spark Connect Session"
            )
        logger.info(f"🚰 Source - Start Load S3: {self.path}")
        self.set_s3_connection(spark=spark)
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


class S3JsonFile(BaseS3File):
    file_format: Literal["json"]
    multiline: bool = False

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        spark: SparkSession = engine["spark"]
        if is_remote_session(spark):
            raise RuntimeError(
                f"Source: {self.type} does not support Spark Connect Session"
            )
        logger.info(f"🚰 Source - Start Load S3: {self.path}")
        self.set_s3_connection(spark=spark)
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
