from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from daft import DataFrame

from pydantic import Field
from pydantic.functional_validators import field_validator

from ... import Result
from ...__types import DictData
from ...models import ColDetail, Context, MetricEngine, MetricTransform
from ..__abc import BaseEngine
from .sink import Sink
from .source import Source
from .transform import Transform

logger = logging.getLogger("jett")


class Daft(BaseEngine):
    """Daft Engine Model."""

    type: Literal["daft"]
    sink: list[Sink] = Field(description="A list of Sink model.")
    source: Source
    transforms: list[Transform] = Field(default_factory=list)

    @field_validator(
        "sink",
        mode="before",
        json_schema_input_type=Sink | list[Sink],
    )
    def __prepare_sink(cls, data: Any) -> Any:
        """Prepare the sink field value that should be list of Sink model."""
        return [data] if not isinstance(data, list) else data

    def execute(
        self,
        context: Context,
        engine: DictData,
        metric: MetricEngine,
    ) -> DataFrame:
        logger.info("Start execute with Arrow engine.")
        df: DataFrame = self.source.handle_load(context, engine=engine)
        df: DataFrame = self.handle_apply(df, context, engine=engine)
        for sk in self.sink:
            sk.handle_save(df, context, engine=engine)
        return df

    def set_engine_context(self, context: Context, **kwargs) -> DictData:
        """Set Daft engine context."""
        return {"engine": self}

    def set_result(self, df: DataFrame, context: Context) -> Result:
        return Result(
            data=[],
            columns=[
                ColDetail(name=f.name, dtype=str(f.dtype)) for f in df.schema()
            ],
            schema_dict={f.name: f.dtype for f in df.schema()},
        )

    def apply(
        self,
        df: DataFrame,
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> DataFrame:
        for op in self.transforms:
            df: DataFrame = op.handle_apply(df, context, engine=engine)
        return df
