from typing import Any, Literal

from pyarrow import Table
from pyarrow.csv import ParseOptions, ReadOptions, read_csv
from pyarrow.dataset import CsvFileFormat, Dataset, dataset
from pyarrow.json import read_json
from pydantic import Field

from .....__types import DictData
from .....models import MetricSource, Shape
from ....__abc import BaseSource


class LocalJsonFileTable(BaseSource):
    type: Literal["local"]
    arrow_type: Literal["table"]
    file_format: Literal["json"]
    path: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Table, Shape]:
        table: Table = read_json(self.path)
        return table, Shape.from_tuple(table.shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalCsvFileTable(BaseSource):
    type: Literal["local"]
    arrow_type: Literal["table"]
    file_format: Literal["csv"]
    path: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Table, Shape]:
        table: Table = read_csv(
            self.path,
            read_options=ReadOptions(
                autogenerate_column_names=True,
            ),
        )
        return table, Shape.from_tuple(table.shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalCsvFileDataset(BaseSource):
    type: Literal["local"]
    arrow_type: Literal["dataset"]
    file_format: Literal["csv"]
    path: str
    partitioning: list[str] | str | None = Field(default=None)

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Dataset, Shape]:
        ds: Dataset = dataset(
            self.path,
            partitioning="hive",
            format=CsvFileFormat(
                **{"parse_options": ParseOptions(delimiter=",")},
            ),
        )
        table = ds.to_table()
        return table, Shape.from_tuple(table.shape)

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalParquetFileDataset(BaseSource):
    type: Literal["local"]
    arrow_type: Literal["dataset"]
    file_format: Literal["parquet"]
    path: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Any, Shape]: ...

    def inlet(self) -> tuple[str, str]: ...
