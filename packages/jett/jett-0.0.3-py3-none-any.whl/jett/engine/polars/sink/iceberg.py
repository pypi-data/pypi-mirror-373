import logging
from typing import Literal

import polars as pl
from polars import DataFrame
from pydantic import Field
from pyiceberg.types import (
    BinaryType,
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    # DurationType,
    FloatType,
    IntegerType,
    ListType,
    LongType,
    # NullType,
    StringType,
    StructType,
    TimestampType,
    TimeType,
)

from ....__types import DictData
from ....models import MetricSink, Shape
from ...__abc import BaseSink
from ..utils import validate_col_allow_snake_case

logger = logging.getLogger("jett")

iceberg_type_mapping = {
    pl.Boolean: BooleanType,
    pl.Int8: IntegerType,
    pl.Int16: IntegerType,
    pl.Int32: IntegerType,
    pl.Int64: LongType,
    pl.UInt8: IntegerType,
    pl.UInt16: IntegerType,
    pl.UInt32: IntegerType,
    pl.UInt64: LongType,
    pl.Float32: FloatType,
    pl.Float64: DoubleType,
    pl.Decimal: DecimalType,
    pl.Utf8: StringType,
    pl.Binary: BinaryType,
    pl.Date: DateType,
    pl.Time: TimeType,
    pl.Datetime: TimestampType,
    # pl.Duration: DurationType,
    pl.List: ListType,
    pl.Categorical: StringType,
    pl.Struct: StructType,
    pl.Object: None,  # Not directly supported
    # pl.Null: NullType,
}


class Iceberg(BaseSink):
    type: Literal["iceberg"]
    mode: Literal["overwrite", "append", "merge"] = Field(
        default="overwrite",
        description=(
            "A write mode that should be `append`, `overwrite`, or `merge` "
            "only."
        ),
    )
    database: str
    table_name: str
    validate_column_snake_case: bool = True

    def save(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricSink,
        **kwargs,
    ) -> tuple[DataFrame, Shape]:
        """Save Polars DataFrame to the Iceberg table.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricSink): A metric sink that was set from handler step
                for passing custom metric data.

        Returns:
            tuple[DataFrame, Shape]:
        """
        logger.info("Sink - Start sink to Iceberg.")
        if df.is_empty():
            logger.warning("Sink - Found empty DataFrame, Skip writing!!!")
            metric.add("affected_partitions", 0)
            return df, Shape(rows=0, columns=0)

        if self.validate_column_snake_case:
            validate_col_allow_snake_case(schema=df.schema)

        return df, Shape()

    def outlet(self) -> tuple[str, str]:
        return "iceberg", self.dest()

    def dest(self) -> str:
        return self.table_name
