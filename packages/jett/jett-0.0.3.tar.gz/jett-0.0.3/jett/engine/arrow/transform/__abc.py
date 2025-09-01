from abc import ABC, abstractmethod

from pyarrow import Schema, Table

from ....__types import DictData
from ....models import MetricOperatorOrder
from ...__abc import BaseTransform


class BaseArrowTransform(BaseTransform, ABC):

    @abstractmethod
    def apply(
        self,
        df: Table,
        engine: DictData,
        metric: MetricOperatorOrder,
        **kwargs,
    ) -> Table: ...

    @staticmethod
    def sync_schema(pre: Schema, post: Schema, metric, **kwargs) -> None: ...
