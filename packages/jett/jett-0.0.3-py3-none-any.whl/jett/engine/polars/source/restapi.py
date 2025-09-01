from typing import Any, Literal

from ....__types import DictData
from ....models import MetricSource, Shape
from ...__abc import BaseSource


class RestApi(BaseSource):
    type: Literal["restapi"]
    host: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Any, Shape]: ...

    def inlet(self) -> tuple[str, str]: ...
