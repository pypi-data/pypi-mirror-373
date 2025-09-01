from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

from ....__types import DictData
from ....models import Shape
from ...__abc import BaseSink

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

logger = logging.getLogger("jett")


class Console(BaseSink):
    """Console Spark Sink model."""

    type: Literal["console"]
    limit: int = 10
    truncate: bool = True

    def save(
        self,
        df: DataFrame,
        engine: DictData,
        **kwargs,
    ) -> Any:
        """Save the result data to the Console."""
        logger.info("🎯 Sink - Start sync with console")
        df.show(self.limit, truncate=self.truncate)
        shape: tuple[int, int] = (df.count(), len(df.columns))
        return df, Shape.from_tuple(shape)

    def outlet(self) -> tuple[str, str]:
        return self.type, self.dest()

    def dest(self) -> str:
        return "console"
