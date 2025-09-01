from typing import Any, Literal

from ....__types import DictData
from ....models import MetricSource, Shape
from ...__abc import BaseSource


class Sdk(BaseSource):
    type: Literal["sdk"]
    cmd: str

    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Any, Shape]: ...

    def inlet(self) -> tuple[str, str]: ...
