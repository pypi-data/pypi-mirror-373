import logging
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from polars import DataFrame

from pydantic import Field
from pydantic.functional_validators import field_validator

from ...__types import DictData
from ...models import ColDetail, Context, MetricEngine, MetricTransform, Result
from ..__abc import BaseEngine
from .sink import Sink
from .source import Source
from .transform import Transform

logger = logging.getLogger("jett")


class Polars(BaseEngine):
    """Polars Engine model."""

    type: Literal["polars"] = Field(description="A type of engine.")
    source: Source
    transforms: list[Transform] = Field(default_factory=list)
    sink: list[Sink] = Field(description="A list of Sink models.")

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
    ) -> "DataFrame":
        """Execute Polars engine method.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricEngine): A metric engine that was set from handler
                step for passing custom metric data.

        Returns:
            DataFrame:
        """
        logger.info("🏗️ Start execute with Polars engine.")
        # NOTE: Start run source handler.
        df: DataFrame = self.source.handle_load(context, engine=engine)

        # NOTE: Start run transform handler.
        df: DataFrame = self.handle_apply(df, context, engine=engine)

        # NOTE: Start multi-sink by sequential strategy.
        for _sink in self.sink:
            _sink.handle_save(df, context, engine=engine)

        return df

    def apply(
        self,
        df: "DataFrame",
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> "DataFrame":
        """Apply Polars engine transformation to the source. This method
        will apply all operators.

        Args:
            df (DataFrame): A Polars DataFrame.
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricTransform): A metric transform that was set from
                handler step for passing custom metric data.
        """
        for t in self.transforms:
            df: DataFrame = t.handle_apply(df, context, engine=engine)
        return df

    def set_result(self, df: "DataFrame", context: Context) -> Result:
        """Set the Result object from executed Polars DataFrame.

        Args:
            df (DataFrame): A Polars DataFrame.
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
        """
        return Result(
            data=[],
            columns=[
                ColDetail(name=name, dtype=str(dtype))
                for name, dtype in df.schema.items()
            ],
            schema_dict=df.schema,
        )

    def set_engine_context(self, context: Context, **kwargs) -> DictData:
        """Set Polars engine context. It will set itself to engine context data.

        Returns:
            A mapping of the engine context data:
                - engine: Self
        """
        return {"engine": self}
