from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from duckdb import DuckDBPyRelation as Relation

import pyarrow as pa
from pydantic import Field

from ...__types import DictData
from ...models import ColDetail, Context, MetricEngine, MetricTransform, Result
from ..__abc import BaseEngine
from .sink import Sink
from .source import Source
from .transform import ListTransform, Transform

logger = logging.getLogger("jett")


class DuckDB(BaseEngine):
    """DuckDB Engine model."""

    type: Literal["duckdb"]
    source: Source = Field(description="A source model.")
    sink: Sink = Field(description="A sink model.")
    transforms: ListTransform = Field(
        default_factory=list,
        description="A list of transform model.",
    )

    def set_engine_context(self, context: Context, **kwargs) -> Any:
        from duckdb.experimental.spark.sql import SparkSession

        return {
            "engine": self,
            "spark": SparkSession.builder.getOrCreate(),
        }

    def execute(
        self, context: Context, engine: DictData, metric: MetricEngine
    ) -> Any:
        """Execute the DuckDB engine.

        Returns:
            Result: A result.
        """
        logger.info("Start execute with DuckDB engine.")
        df: Relation = self.source.handle_load(context, engine=engine)
        df: Relation = self.handle_apply(df, context, engine=engine)
        self.sink.handle_save(df, context, engine=engine)
        return df

    def set_result(self, df: Relation, context: Context) -> Result:
        """Set the Result object for this DuckDB engine.

        Returns:
            Result: A result object.
        """
        arrow_table: pa.Table = df.to_arrow_table()
        schema: pa.Schema = arrow_table.schema
        return Result(
            data=arrow_table.to_pylist(),
            columns=[ColDetail(name=f.name, dtype=str(f.type)) for f in schema],
            schema_dict={f.name: f.type for f in schema},
        )

    def apply(
        self,
        df: Relation,
        context: DictData,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> Relation:
        """Apply transform to the source.

        Args:
            df: Relation
            context: DictData
            engine:
            metric:
        """
        import duckdb

        priority: ListTransform = []
        groups: ListTransform = []
        fallback: ListTransform = []

        logger.debug("Prepare transform analyzer ...")
        for t in self.transforms:
            if t.priority == "pre":
                priority.append(t)
            elif t.priority == "group":
                groups.append(t)
            else:
                fallback.append(t)

        logger.info(f"Priority transform count: {len(priority)}")
        for t in priority:
            logger.info(f"Start priority operator: {t.op!r}")
            df: Relation = t.handle_apply(df, context, engine=engine)

        logger.info(f"Group transform count: {len(groups)}")
        if groups:
            statement_group: list[str] = []
            for g in groups:
                statement_group.append(g.handle_apply_group(df))
            stm: str = f"SELECT {', '.join(statement_group)} FROM df"
            logger.info(f"Statement:\n{stm}")
            df: Relation = duckdb.sql(stm)

        logger.info(f"Fallback transform count: {len(fallback)}")
        for t in fallback:
            logger.info(f"Start fallback operator: {t.op!r}")
            df: Relation = t.handle_apply(df, context, engine=engine)

        return df
