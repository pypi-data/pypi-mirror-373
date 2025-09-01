from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..__types import DictData
from ..models import ALWAYS, EmitCond, MetricData
from .convertor import Convertor


class BaseMetric(BaseModel, ABC):
    """Base Metric abstract model."""

    model_config = ConfigDict(use_enum_values=True)

    type: str = Field(description="A metric type.")
    custom_metric: dict[str, Any] = Field(
        default_factory=dict, description="A custom metric."
    )
    convertor: Convertor = Field(
        default="basic",
        description=(
            "A convertor type that want to prepare metric data before using "
            "on the implemented emit method."
        ),
    )
    condition: EmitCond = Field(
        default=ALWAYS,
        description=(
            "An emitter condition to allow call the emit method after "
            "execution finish."
        ),
    )

    @abstractmethod
    def emit(self, data: MetricData, convert: DictData, **kwargs) -> None:
        """Emit abstraction method for implement egress logic that send the
        metric data after engine execution end.

        Args:
            data (MetricData): A MetricData model that passing after end the
                engine execution.
            convert (DictData): A converted data from the metric data.
        """

    def handle_emit(self, data: MetricData, **kwargs) -> None:
        """Handle Emit method by passing converted data by the convert method.

        Args:
            data (MetricData): A MetricData model instance to pass to emit
                and convert methods.
        """
        covert_data: DictData = self.convert(data)
        self.emit(data=data, convert=covert_data, **kwargs)

    def convert(self, data: MetricData) -> DictData:
        """Convert MetricData to the dict object with specific convertor
        function.

        Args:
            data (MetricData): A MetricData model instance to pass to convert
                methods.
        """
        from .convertor import CONVERTOR_REGISTRY

        if self.convertor not in CONVERTOR_REGISTRY:  # pragma: no cov
            raise NotImplementedError(
                f"Convertor type: {self.convertor!r} does not support."
            )
        return CONVERTOR_REGISTRY[self.convertor](
            data, self.custom_metric
        ).convert()
