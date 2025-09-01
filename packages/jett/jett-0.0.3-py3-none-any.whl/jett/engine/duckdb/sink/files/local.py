from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from duckdb import DuckDBPyRelation as Relation

from pydantic import Field

from jett.__types import DictData
from jett.engine.__abc import BaseSink


class LocalCSVFile(BaseSink):
    """Local file data source."""

    type: Literal["local"]
    file_format: Literal["csv"]
    path: str
    delimiter: str = "|"
    header: bool = Field(default=True)
    sample_records: int | None = 200

    def save(self, df: Relation, *, engine: DictData, **kwargs) -> None:
        file_format: str = Path(self.path).suffix

        if file_format in (".csv",):
            return

        raise NotImplementedError(
            f"Local file format: {file_format!r} does not support yet."
        )

    def outlet(self) -> tuple[str, str]:
        return "csv", self.dest()

    def dest(self) -> str:
        return self.path
