from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from ....__types import DictData
from ....models import Context, MetricOperatorOrder, MetricOperatorTransform
from ...__abc import BaseTransform

if TYPE_CHECKING:
    from polars import DataFrame, DataType, Schema
    from polars import Expr as Column

    PairCol = tuple[Column, str]
    AnyApplyGroupOutput = PairCol | list[PairCol]
    AnyApplyOutput = AnyApplyGroupOutput | DataFrame

logger = logging.getLogger("jett")


def get_map_dtypes() -> dict[str, type[DataType]]:
    import polars as pl

    return {
        "string": pl.String,
        "boolean": pl.Boolean,
        # "integer": ...,
        # "double": ...,
        # "timestamp": ...,
    }


def is_pair_expr(value: PairCol | Any) -> bool:
    """Change value is a pair of Column and string.

    Args:
        value (PairCol | Any): A pair of Column and its name or any value.

    Returns:
        bool: True if an input value is a pair of Column and alias.
    """
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], Column)
        and isinstance(value[1], str)
    )


class BasePolarsTransform(BaseTransform, ABC):
    """Base Polars Transform abstract model"""

    @abstractmethod
    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricOperatorOrder,
        **kwargs,
    ) -> AnyApplyOutput:
        """Apply operator transform abstraction method.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperatorOrder): A metric transform that was set from
                handler step for passing custom metric data.

        Returns:
            AnyApplyOutput: That able to be:
                - PairCol
                - list[PairCol]: A list of pair Expr and alias name.
                - DataFrame: A Polars DataFrame.
        """

    def handle_apply(
        self,
        df: DataFrame,
        context: Context,
        engine: DictData,
        **kwargs,
    ) -> DataFrame:
        """Handle the Operator Apply result output from its custom apply that
        can make different type of result.

        Args:
            df (DataFrame): A Polars DataFrame.
            context: (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            **kwargs:

        Returns:
            DataFrame: A applied Polars DataFrame.
        """
        logger.info(f"👷🔧 Handle Apply Operator: {self.op!r}")
        metric = MetricOperatorOrder(type="order", trans_op=self.op)
        context["metric_operator"].append(metric)
        try:
            pre_schema: Schema = df.schema
            output: AnyApplyOutput = self.apply(
                df, engine=engine, metric=metric, **kwargs
            )
            if is_pair_expr(output):
                df = df.with_columns(output[0].alias(output[1]))
            elif isinstance(output, list) and all(
                is_pair_expr(i) for i in output
            ):
                df = df.with_columns(i[0].alias(i[1]) for i in output)
            elif isinstance(output, DataFrame):
                df: DataFrame = output
            else:
                metric.add(key=self.op, value=output)
                logger.info(f"Set metric from func {self.op} completely")

            # NOTE: Sync schema before return.
            self.sync_schema(pre_schema, df.schema, metric=metric)
            return df
        finally:
            self.post_apply(engine=engine, **kwargs)
            metric.finish()

    @staticmethod
    def sync_schema(
        pre: Schema, post: Schema, metric: MetricOperatorTransform, **kwargs
    ) -> None: ...


class ColMap(BaseModel):
    """Column Map model."""

    name: str = Field(description="A new column name.")
    source: str = Field(
        description="A source column statement before alias with alias.",
    )
