import logging
from typing import Literal

try:
    from daft import DataFrame

    DAFT_EXISTS: bool = True
except ImportError:
    DAFT_EXISTS: bool = False

from ....__types import DictData
from ....models import Shape
from ...__abc import BaseSink

logger = logging.getLogger("jett")


class Console(BaseSink):
    """Console DuckDB Sink model."""

    type: Literal["console"]
    limit: int = 10
    max_width: int | None = None

    def save(
        self,
        df: "DataFrame",
        *,
        engine: DictData,
        **kwargs,
    ) -> tuple["DataFrame", Shape]:
        """Save the result data to the Console."""
        # NOTE: Convert variable from df to table.
        logger.info("🎯 Sink - Start sync with console")
        print(df.show(n=self.limit))
        return df, Shape()

    def outlet(self) -> tuple[str, str]:
        return "console", self.dest()

    def dest(self) -> str:
        return "console"
