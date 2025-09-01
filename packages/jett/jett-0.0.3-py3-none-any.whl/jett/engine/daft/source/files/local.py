from __future__ import annotations

from typing import Literal

try:
    import daft
    from daft import DataFrame

    DAFT_EXISTS: bool = True
except ImportError:
    DAFT_EXISTS: bool = False

from jett.__types import DictData
from jett.engine.__abc import BaseSource
from jett.models import MetricSource, Shape


class LocalJsonFile(BaseSource):
    type: Literal["local"]
    file_format: Literal["json"]
    path: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[DataFrame, Shape]:
        import daft

        df: DataFrame = daft.read_json(
            path=self.path,
            file_path_column=None,
        )
        return df, Shape()

    def inlet(self) -> tuple[str, str]:
        return "local", self.path


class LocalCsvFile(BaseSource):
    type: Literal["local"]
    file_format: Literal["csv"]
    path: str
    delimiter: str | None = None
    header: bool = True

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[DataFrame, Shape]:
        if not DAFT_EXISTS:
            raise ModuleNotFoundError("Does not install daft yet.")

        df: DataFrame = daft.read_csv(
            path=self.path,
            file_path_column=None,
            delimiter=self.delimiter,
            has_headers=self.header,
        )
        return df, Shape()

    def inlet(self) -> tuple[str, str]:
        return "local", self.path
