from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Literal

from ....__types import DictData
from ....models import Context, MetricOperator
from ...__abc import BaseTransform

if TYPE_CHECKING:
    from duckdb import DuckDBPyRelation as Relation
    from duckdb.experimental.spark.sql import DataFrame, SparkSession
    from duckdb.experimental.spark.sql.column import Column

    PairCol = tuple[Column, str]

logger = logging.getLogger("jett")


def is_pair_col(value: PairCol | Any) -> bool:
    """Change value is a pair of Column and string."""
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], Column)
        and isinstance(value[1], str)
    )


class BaseDuckDBTransform(BaseTransform, ABC):
    """Base DuckDB Transform abstract model."""

    priority: Literal["pre", "group", "post"] = "pre"

    @abstractmethod
    def apply(
        self,
        df: Relation | DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> Relation | DataFrame:
        """Apply priority transform."""

    def apply_group(
        self,
        df: Relation | DataFrame,
        engine: DictData,
        metric: MetricOperator,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> str | PairCol | list[PairCol]:
        """Apply group transform."""
        raise NotImplementedError(
            f"Transform: {self.__class__.__name__} on DuckDB engine does not "
            f"implement the group operation, please change this to priority "
            f"operator."
        )

    def handle_apply_group(
        self,
        df: Relation | DataFrame,
        context: Context,
        engine: DictData,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> Any:
        ts: float = time.monotonic()
        metric = MetricOperator(type="order", trans_op=self.op)
        logger.info(f"🔨 Handle Apply Group Operator: {self.op!r}")
        output: str | PairCol | list[PairCol] = self.apply_group(
            df, engine, spark=spark, metric=metric, **kwargs
        )
        if is_pair_col(output):
            rs: dict[str, Column] = {output[1]: output[2]}
        else:
            raise NotImplementedError()
        metric.transform_latency_ms = time.monotonic() - ts
        context["metric_group_transform"].transforms.append(metric)
        return rs

    @staticmethod
    def sync_schema(pre, post, metric, **kwargs) -> None: ...
