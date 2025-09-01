import json
from typing import Any, Literal, TypeVar

from ...models import MetricData


class BaseConvertor:

    def __init__(self, data: MetricData, custom_metric: dict[str, Any]):
        """
        Args:
            data (MetricData): A metric data.
            custom_metric (dict[str, Any]): A custom metric data.
        """
        self.data = data
        self.custom_metric = custom_metric

    def convert(self) -> dict[str, Any]: ...


class BasicConvertor(BaseConvertor):

    def convert(self) -> dict[str, Any]:
        """Covert function with Basic metric data mode."""
        return {
            "run_result": self.data.run_result,
            "execution_time_ms": self.data.execution_time_ms,
            "engine": self.data.metric_engine.model_dump(by_alias=True),
            "source": self.data.metric_source.model_dump(by_alias=True),
            "transform": self.data.metric_transform.model_dump(by_alias=True),
            "sink": self.data.metric_sink.model_dump(by_alias=True),
            "custom_metric": self.custom_metric,
        }


class FullConvertor(BaseConvertor):

    def convert(self) -> dict[str, Any]:
        """Covert function with Full metric data mode."""
        return json.loads(self.data.model_dump_json(by_alias=True)) | {
            "custom_metric": self.custom_metric
        }


Convertor = Literal[
    "basic",
    "full",
]
ConvertType = TypeVar("ConvertType", bound=BaseConvertor)
CONVERTOR_REGISTRY: dict[Convertor, type[ConvertType]] = {
    "full": FullConvertor,
    "basic": BasicConvertor,
}
