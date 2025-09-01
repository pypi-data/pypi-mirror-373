from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Literal, Union

from pydantic import Field

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, SparkSession
    from pyspark.sql.connect.session import DataFrame as DataFrameRemote
    from pyspark.sql.types import StructType

    PairCol = tuple[Column, str]
    AnyDataFrame = DataFrame | DataFrameRemote

from ....__types import DictData
from ....errors import ToolTransformError
from ....models import Context, MetricOperatorGroup, MetricOperatorOrder
from .__abc import BaseSparkTransform, is_pair_col
from .compute_metric import CalculateMinMaxOfColumns, DetectSchemaChangeWithSink
from .cryptography import GCMDecrypt
from .functions import (
    SQL,
    CleanMongoJsonStr,
    DropColumns,
    ExplodeArrayColumn,
    Expr,
    FlattenAllExceptArray,
    JsonStrToStruct,
    RenameColumns,
    RenameSnakeCase,
    Scd2,
)
from .validation import ValidateColumnDisallowSpace

logger = logging.getLogger("jett")

GroupTransform = Annotated[
    Union[RenameColumns,],
    Field(
        discriminator="op",
        description="A transform that allow to use in group operator.",
    ),
]


class Group(BaseSparkTransform):
    """Group Transform model."""

    op: Literal["group"]
    transforms: list[GroupTransform] = Field(
        description=(
            "A list of operator transform model that support for grouping "
            "apply that mean it can execute with parallelism."
        )
    )

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricOperatorGroup,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> AnyDataFrame:
        """Apply to Group operator transform.

        Args:
            df (DataFrame): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperatorOrder): A metric transform that was set from
                handler step for passing custom metric data.
            spark (SparkSession, default None): A Spark session.

        Returns:

        """
        maps: dict[str, Column] = {}
        for t in self.transforms:
            metric_order = MetricOperatorOrder(type="order", trans_op=t.op)
            metric.transforms.append(metric_order)
            try:
                output: PairCol | list[PairCol] = t.apply(
                    df, engine=engine, metric=metric_order, spark=spark
                )

                # VALIDATE: Check the result type that match on the group operator.
                if is_pair_col(output):
                    rs: dict[str, Column] = {output[1]: output[2]}
                elif isinstance(output, list) and all(
                    is_pair_col(i) for i in output
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
        df: DataFrame = df.withColumns(maps)
        return df

    def handle_apply(
        self,
        df: AnyDataFrame,
        context: Context,
        engine: DictData,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> AnyDataFrame:
        """Handle the Group Operator Apply.

        Args:
            df (AnyDataFrame): A Spark DataFrame.
            context: (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.

        Returns:
            AnyDataFrame: A applied Spark DataFrame.
        """
        logger.info(f"👷🔧 Handle Apply Operator: {self.op!r}")
        metric = MetricOperatorGroup(type="group", trans_op=self.op)
        context["metric_operator"].append(metric)
        try:
            pre_schema: StructType = df.schema
            df: DataFrame = self.apply(
                df, engine, metric=metric, spark=spark, **kwargs
            )
            if self.cache:
                logger.warning(
                    f"🏭 Cache the DataFrame after apply operator: {self.op!r}"
                )
                df.cache()
            self.sync_schema(pre_schema, df.schema, metric=metric, spark=spark)
            return df
        finally:
            metric.finish()


Transform = Annotated[
    Union[
        GCMDecrypt,
        Expr,
        SQL,
        DropColumns,
        RenameColumns,
        RenameSnakeCase,
        ExplodeArrayColumn,
        FlattenAllExceptArray,
        Scd2,
        CleanMongoJsonStr,
        JsonStrToStruct,
        ValidateColumnDisallowSpace,
        CalculateMinMaxOfColumns,
        DetectSchemaChangeWithSink,
        Group,
    ],
    Field(
        discriminator="op",
        description="A transform registry",
    ),
]
