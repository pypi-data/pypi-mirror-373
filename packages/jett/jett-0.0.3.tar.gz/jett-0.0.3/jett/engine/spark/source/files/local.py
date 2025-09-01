from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import Field

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

from .....__types import DictData
from .....models import Shape
from .....utils import bool2str
from ....__abc import BaseSource

logger = logging.getLogger("jett")


class LocalCSVFile(BaseSource):
    """Local CSV file data source."""

    type: Literal["local"]
    file_format: Literal["csv"]
    path: str
    delimiter: str = "|"
    header: bool = Field(default=True)
    lazy: bool = True
    sample_records: int | None = 200

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        """Load CSV file to DuckDB Relation object."""
        file_format: str = Path(self.path).suffix
        if file_format not in (".csv",):
            raise NotImplementedError(
                f"Local file format: {file_format!r} does not match with the "
                f"config file format."
            )
        spark: SparkSession = engine["spark"]
        fullpath: str = "file://" + str(Path(self.path).resolve().absolute())
        logger.info(f"🚰 Source - Start Load: {fullpath}")

        df: DataFrame = (
            spark.read.format(self.file_format)
            .option("header", "true" if self.header else "false")
            .option("delimiter", self.delimiter)
            .option("inferSchema", "true")
            .load(fullpath)
        )
        df.show(10, truncate=False)
        shape: tuple[int, int] = (
            0 if self.lazy else df.count(),
            len(df.columns),
        )
        return df, Shape.from_tuple(shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalJsonFile(BaseSource):
    """Local JSON file data source."""

    type: Literal["local"]
    file_format: Literal["json"]
    path: str
    multiline: bool = False
    lazy: bool = True

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        file_format: str = Path(self.path).suffix
        if file_format not in (".json", ".bjson"):
            raise NotImplementedError(
                f"Local file format: {file_format!r} does not match with the "
                f"config file format."
            )
        spark: SparkSession = engine["spark"]
        fullpath: str = "file://" + str(Path(self.path).resolve().absolute())
        logger.info(f"🚰 Source - Start Load: {fullpath}")
        df: DataFrame = (
            spark.read.format(self.file_format)
            .option("inferSchema", "true")
            .option("multiline", bool2str(self.multiline))
            .load(fullpath)
        )
        df.show(10, truncate=False)
        shape: tuple[int, int] = (
            0 if self.lazy else df.count(),
            len(df.columns),
        )
        return df, Shape.from_tuple(shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path
