import logging
from typing import Any, Literal

from pyarrow import Table

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
        df: Table,
        *,
        engine: DictData,
        **kwargs,
    ) -> Any:
        """Save the result data to the Console."""
        # NOTE: Convert variable from df to table.
        table = df
        del df

        logger.info("🎯 Sink - Start sync with console")
        print(table)
        return table, Shape.from_tuple(table.shape)

    def outlet(self) -> tuple[str, str]:
        return "console", self.dest()

    def dest(self) -> str:
        return "console"
