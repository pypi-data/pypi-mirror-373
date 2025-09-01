import logging
from typing import Any, Literal

from pyarrow import Table
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


class Arrow(BaseEngine):
    """Arrow Engine Model.

    This engine support multiple sink.
    """

    type: Literal["arrow"] = Field(description="An engine type.")
    source: Source = Field(description="A Source model.")
    transforms: list[Transform] = Field(
        default_factory=list, description="A list of transform operators."
    )
    sink: list[Sink] = Field(
        description="A list of Sink model.",
        default_factory=list,
    )

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
    ) -> Table:
        """Execute Arrow engine."""
        logger.info("Start execute with Arrow engine.")
        df: Table = self.source.handle_load(context, engine=engine)
        df: Table = self.handle_apply(df, context, engine=engine)
        for sk in self.sink:
            sk.handle_save(df, context, engine=engine)
        return df

    def set_engine_context(self, context: Context, **kwargs) -> DictData:
        return {
            "engine": self,
        }

    def set_result(self, df: Table, context: Context) -> Result:
        return Result(
            data=[],
            columns=[
                ColDetail(name=field.name, dtype=str(field.type))
                for field in df.schema
            ],
            schema_dict={field.name: field.type for field in df.schema},
        )

    def apply(
        self,
        df: Table,
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> Table:
        for op in self.transforms:
            df: Table = op.handle_apply(df, context, engine=engine)
        return df
