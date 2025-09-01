from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daft import DataFrame, Schema

from ....__types import DictData
from ....models import MetricOperatorOrder
from ...__abc import BaseTransform


class BaseDaftTransform(BaseTransform, ABC):

    @abstractmethod
    def apply(
        self,
        df: "DataFrame",
        engine: DictData,
        metric: MetricOperatorOrder,
        **kwargs,
    ) -> "DataFrame":
        """Apply Transform Operation on the Daft DataFrame object."""

    @staticmethod
    def sync_schema(
        pre: "Schema", post: "Schema", metric, **kwargs
    ) -> None: ...
