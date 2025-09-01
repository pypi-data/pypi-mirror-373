from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

from ....__types import DictData
from ..utils import validate_col_disallow_pattern
from .__abc import BaseSparkTransform


class ValidateColumnDisallowSpace(BaseSparkTransform):
    op: Literal["validate_col_names_disallow_whitespace"] = Field(
        description="An operator transform type."
    )

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        *,
        spark: SparkSession | None = None,
        **kwargs,
    ) -> DataFrame:
        """Apply to Validate Column name disallow whitespace.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            spark (SparkSession, default None): A Spark session.

        Returns:
            DataFrame:
        """
        validate_col_disallow_pattern(schema=df.schema, patterns=["whitespace"])
        return df
