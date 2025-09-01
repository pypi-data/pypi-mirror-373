from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from .....__types import DictData
from .....models import Shape
from ....__abc import BaseSource

if TYPE_CHECKING:
    from polars import DataFrame


class LocalCSVFile(BaseSource):
    """Local file system with CSV file format source model."""

    type: Literal["local"] = Field(description="A type of source.")
    file_format: Literal["csv"] = Field(description="A file format.")
    path: str
    delimiter: str = "|"
    header: bool = Field(default=True)
    sample_records: int | None = 200

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        """Load CSV file to DuckDB Relation object."""
        import polars as pl

        file_format: str = Path(self.path).suffix
        if file_format not in (".csv",):
            raise NotImplementedError(
                f"Local file format: {file_format!r} does not support."
            )
        df: DataFrame = pl.read_csv(
            source=self.path,
            separator=self.delimiter,
            has_header=self.header,
            sample_size=self.sample_records,
        )
        return df, Shape.from_tuple(df.shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalJsonFile(BaseSource):
    """Local JSON file data source."""

    type: Literal["local"]
    file_format: Literal["json", "ndjson"]
    path: str

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        """Load JSON file from local file system."""
        import polars as pl

        file_format: str = Path(self.path).suffix
        if file_format not in (".json",):
            raise NotImplementedError(
                f"Local file format: {file_format!r} does not support."
            )

        if self.file_format == "ndjson":
            df: DataFrame = pl.read_ndjson(source=self.path)
        else:
            df: DataFrame = pl.read_json(source=self.path)
        return df, Shape.from_tuple(df.shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path
