from typing import Any, Literal

from pydantic import Field

from ... import Result
from ...__types import DictData
from ...models import Context, MetricEngine, MetricTransform
from ..__abc import BaseEngine


class Dbt(BaseEngine):
    type: Literal["dbt"]
    profile: str = Field(description="A DBT profile YAML filepath.")
    project: str = Field(description="A DBT project YAML filepath.")

    def ping(self) -> bool:
        """Ping the DBT profile and project location."""

    def execute(
        self,
        context: Context,
        engine: DictData,
        metric: MetricEngine,
    ) -> Any: ...

    def set_engine_context(self, context: Context, **kwargs) -> DictData:
        return {"engine": self}

    def set_result(self, df: Any, context: Context) -> Result:
        return Result()

    def apply(
        self,
        df: Any,
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> Any:
        return df
