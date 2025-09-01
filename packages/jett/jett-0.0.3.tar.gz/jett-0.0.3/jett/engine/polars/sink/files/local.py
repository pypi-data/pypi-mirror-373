from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from jett.engine.__abc import BaseSink

if TYPE_CHECKING:
    from polars import DataFrame


class LocalCSVFile(BaseSink):
    """Local file data source."""

    type: Literal["local"]
    file_format: Literal["csv"]
    path: str
    delimiter: str = "|"
    header: bool = Field(default=True)
    sample_records: int | None = 200

    def save(self, df: DataFrame, *, engine, **kwargs) -> None:
        file_format: str = Path(self.path).suffix

        if file_format in (".csv",):
            return

        # df.write_csv(self.path, separator=self.delimiter)

        raise NotImplementedError(
            f"Local file format: {file_format!r} does not support yet."
        )

    def outlet(self) -> tuple[str, str]:
        return "csv", self.dest()

    def dest(self) -> str:
        return self.path
