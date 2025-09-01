from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.types import StructField

from .....utils import clean_string, get_dt_now

logger = logging.getLogger("jett")


class TableMaintenance(BaseModel):
    """Maintenance Utility Model for Iceberg Table

    :param database: db name
    :param table_name: table name
    :param retention_days: a number of days that we will retain the data in the table
    :param retention_key: a timestamp column which will be used to filter data to be deleted
    :param keep_snapshot_days: a number of days that we will keep the snapshots,
        the snapshots that day older than param will be deleted
    :param keep_snapshot_at_least: a number of snapshots which will be retained after snapshot's expiration procedure
    """

    database: str = Field(description="A database name.")
    table_name: str = Field(description="A table name.")
    retention_days: int | None = None
    retention_key: str | None = None
    keep_snapshot_days: int | None = None
    keep_snapshot_at_least: int | None = None

    def validate_retention_key(self, df: DataFrame) -> None:
        """Validate retention key, it must be a timestamp column."""
        from pyspark.sql.types import TimestampType

        if self.retention_days is None:
            return

        found_col: list[StructField] = [
            col for col in df.schema if col.name == self.retention_key
        ]
        if len(found_col) == 0:
            raise ValueError(
                f"retention key: {self.retention_key} not found in DataFrame"
            )

        if not isinstance(found_col[0].dataType, TimestampType):
            raise ValueError(
                f"retention key: {self.retention_key} is not a timestamp column"
            )

    @staticmethod
    def _calculate_past_date(days: int) -> str:
        """
        calculate past datetime and result as date with hh:mm:ss of 00:00:00
        """
        current_ts = get_dt_now()
        new_ts = current_ts - timedelta(days=days)
        new_ts = new_ts.date()
        new_ts = f"{new_ts} 00:00:00"
        return new_ts

    def is_snapshot_outdated(self, spark: SparkSession) -> bool:
        """
        check is snapshot outdated
        """
        expired_at = self._calculate_past_date(days=self.keep_snapshot_days)
        sql = f"""
        SELECT COUNT(*) AS cnt FROM {self.database}.{self.table_name}.snapshots
        WHERE committed_at < '{expired_at}'
        """
        result = spark.sql(sql).collect()
        result = result[0]

        is_outdated = False
        if result.cnt > 0:
            is_outdated = True

        return is_outdated

    def expire_snapshot(self, spark: SparkSession) -> None:
        """
        expire snapshots that are older than given number of keep_snapshot_days
        """
        is_outdated = self.is_snapshot_outdated(spark=spark)
        if is_outdated:
            expired_at = self._calculate_past_date(days=self.keep_snapshot_days)
            logger.info("expire snapshots older than: %s", expired_at)
            catalog = spark.catalog.currentCatalog()
            retain_sql = f"""
            CALL {catalog}.system.expire_snapshots(
                '{self.database}.{self.table_name}',
                TIMESTAMP '{expired_at}',
                {self.keep_snapshot_at_least}
            )
            """
            retain_sql = clean_string(text=retain_sql)
            logger.info(retain_sql)
            result = spark.sql(retain_sql).collect()
            result = result[0]
            logger.info(
                "number of data files deleted: %s",
                result.deleted_data_files_count,
            )
            logger.info(
                "number of position files deleted: %s",
                result.deleted_position_delete_files_count,
            )
            logger.info(
                "number of equality files deleted: %s",
                result.deleted_equality_delete_files_count,
            )
            logger.info(
                "number of manifest files deleted: %s",
                result.deleted_manifest_files_count,
            )
            logger.info(
                "number of manifest list files deleted: %s",
                result.deleted_manifest_lists_count,
            )

    def retain_data(self, spark: SparkSession) -> None:
        """Retain data based on number of days."""
        if self.retention_days is None:
            return
        retain_at = self._calculate_past_date(days=self.retention_days)
        logger.info("delete data older than: %s", retain_at)
        delete_sql = f"""
        DELETE FROM {self.database}.{self.table_name}
        WHERE {self.retention_key} < '{retain_at}'
        """
        delete_sql = clean_string(text=delete_sql)
        logger.info(delete_sql)
        spark.sql(delete_sql)
