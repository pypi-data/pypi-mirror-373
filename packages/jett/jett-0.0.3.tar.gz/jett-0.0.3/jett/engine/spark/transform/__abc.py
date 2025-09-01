from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, SparkSession
    from pyspark.sql.connect.column import Column as ColumnRemote
    from pyspark.sql.connect.session import DataFrame as DataFrameRemote
    from pyspark.sql.types import StructType

    PairCol = tuple[Column, str]
    AnyDataFrame = DataFrame | DataFrameRemote
    AnyApplyGroupOutput = PairCol | list[PairCol]
    AnyApplyOutput = AnyApplyGroupOutput | AnyDataFrame

from ....__types import DictData
from ....errors import ToolTransformError
from ....models import (
    Context,
    MetricOperator,
    MetricOperatorOrder,
    MetricOperatorTransform,
)
from ....utils import sort_non_sensitive_str
from ...__abc import BaseTransform
from ..utils import extract_cols_without_array, schema2dict

logger = logging.getLogger("jett")


def is_pair_col(value: Any) -> bool:
    """Change value is a pair of Column and string.

    Args:
        value (Any): A pair of Column and its name or any value.

    Returns:
        bool: True if an input value is a pair of Column and alias.
    """
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and isinstance(value[0], (Column, ColumnRemote))
        and isinstance(value[1], str)
    )


class BaseSparkTransform(BaseTransform, ABC):
    """Base Spark Transform abstract model."""

    priority: Literal["pre", "group", "post"] = Field(
        default="pre",
        description=(
            "A priority value for order transform operator before apply. "
            "This field will deprecate in the future and move to use `group` "
            "operator instead."
        ),
    )
    cache: bool = Field(
        default=False,
        description="Use `.cache` method to applied Spark DataFrame if it set.",
    )

    @abstractmethod
    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricOperatorOrder,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> AnyApplyOutput:
        """Apply operator transform abstraction method.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperatorOrder): A metric transform that was set from
                handler step for passing custom metric data.
            spark (SparkSession, default None): A Spark session.

        Returns:
            AnyApplyOutput: An any applied output that can be
                - PairCol: A pair of Column and its alias name.
                - list[PairCol]: A list of pair Column.
                - DataFrame: A Spark DataFrame.
        """

    def apply_group(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricOperator,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> AnyApplyGroupOutput:
        """Apply group transform method that is optional apply for supported
        group transform model.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperator): A metric transform that was set from
                handler step for passing custom metric data.
            spark (SparkSession, default None): A Spark session.

        Returns:
            AnyApplyGroupOutput: An any applied group output that can be
                - PairCol: A pair of Column and its alias name.
                - list[PairCol]: A list of pair Column.
        """
        raise NotImplementedError(
            f"Transform: {self.__class__.__name__} on Spark engine does not "
            f"implement the group operation, please change this to priority "
            f"operator."
        )

    def handle_apply_group(
        self,
        df: DataFrame,
        context: Context,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> dict[str, Column]:
        """Handle Apply group transform.

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
            dict[str, Column]: A mapping of alias name and Column object.
        """
        logger.info(f"👷🔨 Handle Apply Group Operator: {self.op!r}")
        metric = MetricOperator(type="order", trans_op=self.op)
        context["metric_group_transform"].transforms.append(metric)
        try:
            output: PairCol | list[PairCol] = self.apply_group(
                df, engine, metric=metric, spark=spark, **kwargs
            )
            if is_pair_col(output):
                rs: dict[str, Column] = {output[1]: output[0]}
            elif isinstance(output, list) and all(
                is_pair_col(i) for i in output
            ):
                rs: dict[str, Column] = {p[1]: p[0] for p in output}
            else:
                raise ToolTransformError(
                    "Transform group on Spark engine should return the apply group "
                    "result with a pair of Column and str only"
                )
            if self.cache:
                logger.warning(
                    f"🏭 Cache the DataFrame after apply operator: {self.op!r}"
                )
                df.cache()
            return rs
        finally:
            self.post_apply(engine=engine, **kwargs)
            metric.finish()

    def handle_apply(
        self,
        df: AnyDataFrame,
        context: Context,
        engine: DictData,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> AnyDataFrame:
        """Handle the Operator Apply result output from its custom apply that
        can make different type of result. It can be Column, DataFrame, or
        a pair of Column and its alias name.

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
        metric = MetricOperatorOrder(type="order", trans_op=self.op)
        context["metric_operator"].append(metric)
        try:
            pre_schema: StructType = df.schema
            output: AnyApplyOutput = self.apply(
                df, engine=engine, metric=metric, **kwargs
            )
            if is_pair_col(output):
                df = df.withColumn(output[1], output[0])
            elif isinstance(output, list) and all(
                is_pair_col(i) for i in output
            ):
                df = df.withColumns({i[1]: i[0] for i in output})
            elif isinstance(output, (DataFrame, DataFrameRemote)):
                df: AnyDataFrame = output
            else:
                metric.add(key=self.op, value=output)
                logger.info(f"Set metric from func {self.op} completely")

                # ARCHIVE:
                # raise ToolTransformError(
                #     "Transform priority or fallback on Spark engine should return "
                #     "the apply result with type in a pair of Column, a list of "
                #     "pair of Column, or DataFrame only"
                # )
            if self.cache:
                logger.warning(
                    f"🏭 Cache the DataFrame after apply operator: {self.op!r}"
                )
                df.cache()

            # NOTE: Sync schema before return.
            self.sync_schema(pre_schema, df.schema, metric=metric, spark=spark)
            return df
        finally:
            self.post_apply(engine, **kwargs)
            metric.finish()

    @staticmethod
    def sync_schema(
        pre: StructType,
        post: StructType,
        *,
        metric: MetricOperatorTransform,
        spark: SparkSession | None = None,
    ) -> None:
        """Sync schema change to the metric transform.

        Args:
            pre (StructType): A pre schema before apply.
            post (StructType): A post schema that have applied.
            metric (MetricOperatorTransform): An operator transform metric model
                that want to update schema pre and post for tracking change.
            spark (SparkSession, default None): A Spark session.
        """
        pre_schema = spark.createDataFrame(data=[], schema=pre).schema
        post_schema = spark.createDataFrame(data=[], schema=post).schema
        pre_no_array = sort_non_sensitive_str(
            extract_cols_without_array(schema=pre_schema)
        )
        post_no_array = sort_non_sensitive_str(
            extract_cols_without_array(schema=post_schema)
        )
        # NOTE: Start update the pre- and post-schema metric.
        metric.transform_pre = {
            "schema": schema2dict(pre, sorted_by_name=True),
            "schema_no_array": pre_no_array,
        }
        metric.transform_post = {
            "schema": schema2dict(post, sorted_by_name=True),
            "schema_no_array": post_no_array,
        }
