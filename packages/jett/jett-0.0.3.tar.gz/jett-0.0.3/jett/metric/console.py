from __future__ import annotations

import json
import logging
from typing import Literal

from pydantic import Field

from ..__types import DictData
from ..models import MetricData
from .__abc import BaseMetric

logger = logging.getLogger("jett")


class Console(BaseMetric):
    """Console Metric model that use to emit metric to logging with a specific
    logging name.
    """

    type: Literal["console"] = Field(description="A type of console metric.")
    name: str = Field(default="jett", description="A logging name.")

    def emit(self, data: MetricData, convert: DictData, **kwargs) -> None:
        """Emit Console method.

        Args:
            data (MetricData): A MetricData model that passing after end the
                engine execution.
            convert (DictData): A converted data from the metric data.
        """
        logger.info("📩 Metric - console")
        console = logging.getLogger(self.name)
        console.info(
            f"Console Metric:\n{json.dumps(convert, default=str, indent=1)}"
        )
