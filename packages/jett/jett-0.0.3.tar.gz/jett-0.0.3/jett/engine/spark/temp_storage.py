from __future__ import annotations

import logging
import os
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.connect.session import SparkSession as SparkRemoteSession
    from pyspark.sql.types import StructType

    AnySparkSession = SparkSession | SparkRemoteSession

from jett.utils import get_random_str, spark_env

from .utils import is_remote_session

logger = logging.getLogger("jett")


class TempStorage:
    """Temp Storage class for managing the DataFrame to temporary storage."""

    def __init__(
        self,
        spark: AnySparkSession,
        *,
        prefix: str | None = None,
    ) -> None:
        self.spark = spark
        self.temp_dir = self.get_temp_dir(prefix or "")
        self.is_written: bool = False

    def get_temp_dir(self, prefix: str) -> str:
        """Get the random string and set the temporary directory.

        Args:
            prefix (str): A prefix of dir.
        """
        dir_name: str = f"{prefix}" if prefix != "" else ""
        if is_remote_session(self.spark):
            dir_name = f"spark__connect__{dir_name}"

        if dir_name != "" and not dir_name.endswith("__"):
            dir_name = f"{dir_name}__"
        return os.path.join(
            spark_env("SPARK_TEMP_DIR"),
            f"{dir_name}{get_random_str(n=20)}",
        )

    def apply(
        self,
        df: DataFrame,
        override_schema: StructType = None,
    ) -> DataFrame:
        """Write data to temporary directory and load the data from the
        temporary directory.
        """
        logger.info(f"Write DataFrame to temporary directory: {self.temp_dir}")
        df.write.format("parquet").mode("overwrite").save(self.temp_dir)

        logger.info(f"Load DataFrame from: {self.temp_dir}")
        if override_schema is not None:
            df = self.spark.read.schema(override_schema).parquet(self.temp_dir)
        else:
            df = self.spark.read.parquet(self.temp_dir)
        self.is_written = True
        return df

    def teardown(self) -> None:
        """Clean the temporary directory."""
        if self.temp_dir is None or not self.is_written:
            return

        logger.info(f"Clean temporary directory: {self.temp_dir}")
        env: str = spark_env("ENV", default="")
        if env == "aws":
            self.__overwrite_temp_dir_with_empty()
        elif env == "iu":
            if is_remote_session(spark=self.spark):
                self.__overwrite_temp_dir_with_empty()
            else:
                self.__clean_temp_dir_via_spark_context()
        elif env == "local":
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            logger.info(f"⚠️ Directory {self.temp_dir} is deleted")
        else:
            raise RuntimeError(
                f"not implemented for spark env:{env}",
            )

    def __overwrite_temp_dir_with_empty(self) -> None:
        """Clean temp directory on the target dir via overwrite empty DataFrame.

        Warnings:
            This is just a temporary solution for any non-support valid
        `clean_temp_dir` process, this method will only overwrite temp_dir with
        empty dataframe for reducing usage of storage.
        """
        from pyspark.sql.types import StringType, StructField, StructType

        logger.info(
            "overwrite directory %s with empty dataframe data file",
            self.temp_dir,
        )
        empty_df = self.spark.createDataFrame(
            [], schema=StructType([StructField("dummy_col", StringType())])
        )
        empty_df.write.format("parquet").mode("overwrite").save(self.temp_dir)

    def __clean_temp_dir_via_spark_context(self) -> None:
        """Clean temp directory on the HDFS via Spark context."""
        sc = self.spark.sparkContext
        # ignore pylint protected-access
        fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(
            sc._jsc.hadoopConfiguration()
        )
        if fs.exists(sc._jvm.org.apache.hadoop.fs.Path(self.temp_dir)):
            fs.delete(sc._jvm.org.apache.hadoop.fs.Path(self.temp_dir))
            logger.info(f"⚠️ Directory {self.temp_dir} is deleted")
