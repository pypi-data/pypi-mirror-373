from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Any, Literal, Union, get_type_hints

from pydantic import Field
from pydantic.functional_validators import field_validator

from ....__types import DictData
from ....errors import ToolTransformError
from ....models import Context, MetricOperatorGroup, MetricOperatorOrder
from .__abc import BasePolarsTransform, is_pair_expr
from .functions import (
    ExplodeArrayColumn,
    FlattenAllExceptArray,
    RenameColumns,
    RenameSnakeCase,
    Sql,
)
from .functions import Expr as ExprTransform

if TYPE_CHECKING:
    from polars import DataFrame, Schema
    from polars import Expr as Column

    PairCol = tuple[Column, str]

logger = logging.getLogger("jett")

GroupTransform = Annotated[
    Union[ExprTransform,],
    Field(
        discriminator="op",
        description="A transform that allow to use in group operator.",
    ),
]


class Group(BasePolarsTransform):
    """Group Transform model."""

    op: Literal["group"]
    transforms: list[GroupTransform] = Field(
        description=(
            "A list of operator transform model that support for grouping "
            "apply that mean it can execute with parallelism."
        )
    )

    # ARCHIVE:
    # @field_validator("transforms", mode="after")
    # def __validate_supported_output_type(
    #     cls,
    #     data: list[GroupTransform],
    # ) -> list[GroupTransform]:
    #     for t in data:
    #         hints: dict[str, Any] = get_type_hints(t)
    #         if (
    #             'return' in hints
    #             and (rt := hints['return'])
    #             and (
    #                 isinstance(rt, DataFrame)
    #                 or (
    #                     isinstance(rt, list)
    #                     and any(isinstance(i, DataFrame) for i in rt)
    #                 )
    #             )
    #         ):
    #             raise ValueError(
    #                 f"Group operator transform does not support operator: {t}."
    #             )
    #     return data

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricOperatorGroup,
        **kwargs,
    ) -> DataFrame:
        """Apply to Group operator transform.

        Args:
            df (Any): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperatorOrder): A metric transform that was set from
                handler step for passing custom metric data.

        Returns:

        """
        maps: dict[str, Column] = {}
        for t in self.transforms:
            metric_order = MetricOperatorOrder(type="order", trans_op=t.op)
            metric.transforms.append(metric_order)
            try:
                output: PairCol | list[PairCol] | Any = t.apply(
                    df, engine=engine, metric=metric_order
                )

                # VALIDATE: Check the result type that match on the group operator.
                if is_pair_expr(output):
                    rs: dict[str, Column] = {output[1]: output[0]}
                elif isinstance(output, list) and all(
                    is_pair_expr(i) for i in output
                ):
                    rs: dict[str, Column] = {p[1]: p[0] for p in output}
                else:
                    raise ToolTransformError(
                        "Group on Spark engine should return the apply"
                        "group result with a pair of Column and str only."
                    )
                maps.update(rs)
            finally:
                metric_order.finish()
        df: DataFrame = df.with_columns(maps)
        return df

    def handle_apply(
        self,
        df: DataFrame,
        context: Context,
        engine: DictData,
        **kwargs,
    ) -> DataFrame:
        """Handle the Group Operator Apply.

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

        Returns:
            DataFrame: A applied Spark DataFrame.
        """
        logger.info(f"👷🔧 Handle Apply Operator: {self.op!r}")
        metric = MetricOperatorGroup(type="group", trans_op=self.op)
        context["metric_operator"].append(metric)
        try:
            pre_schema: Schema = df.schema
            df: DataFrame = self.apply(df, engine, metric=metric, **kwargs)
            self.sync_schema(pre_schema, df.schema, metric=metric)
            return df
        finally:
            metric.finish()


Transform = Annotated[
    Union[
        ExplodeArrayColumn,
        RenameSnakeCase,
        RenameColumns,
        Sql,
        ExprTransform,
        FlattenAllExceptArray,
    ],
    Field(discriminator="op"),
]
