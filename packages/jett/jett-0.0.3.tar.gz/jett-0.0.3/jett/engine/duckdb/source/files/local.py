from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from duckdb import DuckDBPyRelation

from pydantic import Field

from .....__types import DictData
from .....models import MetricSource, Shape
from ....__abc import BaseSource


class LocalCsvFile(BaseSource):
    """Local CSV file data source."""

    type: Literal["local"]
    file_format: Literal["csv"]
    path: str
    delimiter: str = "|"
    header: bool = Field(default=True)
    sample_records: int | None = 200

    def load(
        self, engine: DictData, metric: MetricSource, **kwargs
    ) -> tuple["DuckDBPyRelation", Shape]:
        """Load CSV file to DuckDB Relation object."""
        import duckdb

        file_format: str = Path(self.path).suffix
        if file_format not in (".csv",):
            raise NotImplementedError(
                f"Local file format: {file_format!r} does not support."
            )
        df = duckdb.read_csv(
            path_or_buffer=self.path,
            delimiter=self.delimiter,
            header=self.header,
            sample_size=self.sample_records,
        )
        return df, Shape.from_tuple(df.shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalJsonFile(BaseSource):
    """Local JSON file data source."""

    type: Literal["local"]
    file_format: Literal["json"]
    path: str = Field(description="A path of local JSON file.")
    format: Literal["newline_delimited", "array"] = "newline_delimited"

    def load(
        self, engine: DictData, metric: MetricSource, **kwargs
    ) -> tuple["DuckDBPyRelation", Shape]:
        import duckdb

        file_format: str = Path(self.path).suffix
        if file_format not in (".json",):
            raise NotImplementedError(
                f"Local file format: {file_format!r} does not support."
            )
        # ARCHIVE:
        # df = duckdb.sql(
        #     f"""SELECT * FROM read_json_objects(
        #         '{self.path}'
        #         , format = '{self.format}'
        #     ) AS original_data
        #     """
        # )
        df = duckdb.read_json(path_or_buffer=self.path, format=self.format)
        return df, Shape.from_tuple(df.shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path
