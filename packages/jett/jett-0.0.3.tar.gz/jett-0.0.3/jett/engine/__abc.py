"""Abstraction module for keeping necessary abstract model class that making
from ABC and BaseModel.

AbstractClasses:
    BaseEngine: A Base abstraction model and class for any implemented engine.
        The engine is the main model for all abstraction model.
    BaseSource: A Base abstraction model and class for any implemented source
        base on its specific engine.
    BaseTransform: A Base abstraction model and class for any implemented
        transform operator base on its specific engine.
    BaseSink: A Base abstraction model and class for any implemented sink
        base on its specific engine.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Literal, get_args, get_origin

from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator

from ..__types import DictData
from ..metric import Metric
from ..models import (
    ALWAYS,
    ONLY_FAILED,
    ONLY_SUCCESS,
    Context,
    MetricData,
    MetricEngine,
    MetricOperatorGroup,
    MetricOperatorOrder,
    MetricSink,
    MetricSource,
    MetricTransform,
    Result,
    Shape,
)

logger = logging.getLogger("jett")


class BaseEngine(BaseModel, ABC):
    """Base Engine abstract model for any implemented engine of Tool opterator.
    This model use handler concept.

    AbstractMethods:
        set_engine_context:
        apply:
        execute:
        set_result: Set the Result object from the output of execution.

    Methods:
        handle_execute:
        handle_apply:
        emit:
        post_execute:
    """

    type: str = Field(
        description=(
            "A engine type that will force to set some specific literal string "
            "values."
        )
    )
    name: str = Field(
        description="A name of this engine template session.",
        json_schema_extra={"title": "Name"},
    )
    app_name: str | None = Field(
        default=None,
        description=(
            "An application name that will use on the target engine session if "
            "it need to define."
        ),
    )
    author: list[str] = Field(
        default_factory=list,
        json_schema_extra={
            "title": "Author",
            "description": "An author name of this Tool configuration template",
        },
    )
    owner: list[str] = Field(
        default_factory=list,
        json_schema_extra={
            "title": "Owner",
            "description": "Owner name of this requirement.",
        },
    )
    tags: list[str] = Field(
        default_factory=list,
        description="A list of tag that will help to find a group of template.",
    )
    parent_dir: Path | None = Field(
        default=None,
        description="A parent directory of that configuration location.",
    )
    metrics: list[Metric] = Field(
        default_factory=list,
        description="A list of metric model that want to emit result.",
    )

    @field_validator(
        "author",
        "owner",
        mode="before",
        json_schema_input_type=str | list[str] | None,
    )
    def __convert_str_to_list_of_str(cls, data: Any) -> Any:
        if data and isinstance(data, str):
            return [data]
        return data

    @field_validator("parent_dir", mode="before", json_schema_input_type=str)
    def __cast_str_to_path(cls, data: Any) -> Any:
        """Cast type of the `parent_dir` field. It will convert to Path object
        if it passes with string type.

        Args:
            data (Any): An any data that pass before validation.
        """
        return Path(data) if data and isinstance(data, str) else data

    @abstractmethod
    def execute(
        self,
        context: Context,
        engine: DictData,
        metric: MetricEngine,
    ) -> Any:
        """Abstract execute method for any engine should implement before
        plugin to this package.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricEngine): A metric engine that was set from handler
                step for passing custom metric data.

        Notes:
            It same some recommended rule that it should to follow:
            - Should to use `handle_{layer}` method like
                - `handle_load`
                - `handle_apply`
                - `handle_save`
              instead of use its method directly.
            - Execution should not create any context. That mean the handle
              will do this task.

        Returns:
            Any: An Any DataFrame API specific with implemented engine.
        """

    @abstractmethod
    def set_result(self, df: Any, context: Context) -> Result:
        """Abstract set a Result object before returning from the handle_execute
        method. The method should implement from sub-model of this `BaseEngine`.

        Args:
            df (Any): An Any DataFrame API.
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config model.
        """

    @abstractmethod
    def apply(
        self,
        df: Any,
        context: Context,
        engine: DictData,
        metric: MetricTransform,
        **kwargs,
    ) -> Any:
        """Abstract apply method for start running the engine transform for each
        operator.

        Args:
            df (Any):
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

    def post_execute(
        self,
        context: Context,
        *,
        engine: DictData,
        exception: Exception | None = None,
        **kwargs,
    ) -> Any:
        """Overridable Post Execute method.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            exception (Exception | None, default is None) An exception object if
                the returning execute method raise some error while executing.

        Returns:
            Any: An any output that will update to the context with key
                `post_execution_output`.
        """

    @abstractmethod
    def set_engine_context(self, context: Context, **kwargs) -> DictData:
        """Set Engine Context data for passing to execute method.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.

        Returns:
            DictData: An any engine context data.
        """

    def handle_execute(self, context: Context) -> Result:
        """Handle execute method with preparing any DataFrame API to the Result
        object. This method must call from the Tool Operator execute method.

            This engine handler execute method will pre-define engine metric
        before call abstract execute method.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.

        Raises:
            Exception: An any exception that is able to catch from the `execute`
                or `set_result` methods.

        Returns:
            Result: A Result model that catch from the sink DataFrame API info.
        """
        name: str = self.app_name or self.name
        logger.info(f"👷🏗️ Handle Execute config name: {name!r} ...")
        metric = MetricEngine(app_id=name, type=self.type)
        context.update({"metric_engine": metric})
        engine: DictData = self.set_engine_context(context)
        exception: Exception | None = None
        try:
            rs = self.execute(context, engine=engine, metric=metric)
            return self.set_result(rs, context)
        except Exception as e:
            exception = e
            logger.exception(
                f"Catch error from the engine execution: {e.__class__.__name__}"
            )
            raise
        finally:
            logger.warning("Start Post execution and update metric extra ...")
            post_output: Any = self.post_execute(
                context, engine=engine, exception=exception
            )
            metric.finish()
            context.update(
                {
                    "metric_extras": engine.pop("metric_extras", {}),
                    "post_execution_output": post_output,
                }
            )

    def handle_apply(
        self,
        df: Any,
        context: Context,
        engine: DictData,
        **kwargs,
    ) -> Any:
        """Handle Apply Engine transform method. This method will update
        necessary transform metrics before and catch up it after apply.

            This handle method will update `metric_operator` and `metric_group_transform`
        keys to the context object before start its apply method. After apply,
        it will prepare the keys that set before to `metric_transform` key

        Args:
            df (Any): An any DataFrame API that use to apply transform.
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.

        Returns:
            Any: Return an any DataFrameAPI that was applied with all transform
                operator.
        """
        metric = MetricTransform()
        metric_op_group = MetricOperatorGroup(type="group")
        context.update(
            {
                "metric_transform": metric,
                "metric_operator": [],
                "metric_group_transform": metric_op_group,
            }
        )
        try:
            df: Any = self.apply(
                df, context, engine=engine, metric=metric, **kwargs
            )
            return df
        except Exception as e:
            logger.error(
                f"Catch error from the engine apply: {e.__class__.__name__}"
            )
            raise
        finally:
            metric_op_group.finish()
            metric.transforms = context.get("metric_operator", [])
            metric.finish()

    def emit(self, context: Context) -> None:
        """Emit metric data to each metric model with the current context data.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
        """
        data = MetricData.model_validate(context)
        for metric in self.metrics:
            if metric.condition != ALWAYS and (
                (metric.condition == ONLY_FAILED and data.run_result)
                or (metric.condition == ONLY_SUCCESS and not data.run_result)
            ):
                continue
            try:
                logger.info(
                    f"👷🏗📩 Handler Emit with metric type: {metric.type!r}"
                )
                metric.handle_emit(data=data, **context)
            except Exception as e:
                logger.exception(
                    f"‼️ Error occurred when trying to push metric: "
                    f"{metric.type!r} with err: {e.__class__.__name__}, "
                    f"continue to next emitter\n... {e}"
                )


class BaseSource(BaseModel, ABC):
    """Base Source abstract model."""

    type: str = Field(description="A source type.")
    sample_records: int | None = Field(
        default=None,
        description="A sample records value that use to limit data after load.",
        ge=0,
        le=10_000,
    )

    @field_validator("sample_records")
    def check_range(cls, value: Any) -> Any:
        """Validate number of sample records."""
        if value is not None and (value < 0 or value > 10_000):
            raise ValueError(
                "sample record should has range between 0 and 10000"
            )
        return value

    @abstractmethod
    def load(
        self,
        engine: DictData,
        metric: MetricSource,
        **kwargs,
    ) -> tuple[Any, Shape]:
        """Load abstract method for this source model.

        Args:
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricSource): A metric source that was set from handler
                step for passing custom metric data.
        """

    @abstractmethod
    def inlet(self) -> tuple[str, str]:
        """Return a pair of type and name of the inlet data for the event hub
        service for create data lineage together with the outlet of sink.

        Returns:
            tuple[str, str]: A pair of type and this source name.
        """

    def handle_load(
        self,
        context: Context,
        *,
        engine: DictData | None = None,
        **kwargs,
    ) -> Any:
        """Handle load method with adding source metric to the execution
        context.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
        """
        logger.info(f"👷🚰 Handle Source: {self.type!r} ...")
        metric = MetricSource(type=self.type, inlet=self.inlet())
        context.update({"metric_source": metric})
        try:
            df, shape = self.load(engine=engine, metric=metric, **kwargs)
            metric.read_row_count = shape.rows
            metric.read_column_count = shape.columns
            return df
        finally:
            metric.finish()


class BaseTransform(BaseModel, ABC):
    """Base Transform abstract model for any implemented transform operator
    for each engine. That mean the transform operator have different supported
    operator base on engine that it implemented for.

    AbstractMethods:
        apply:

    Methods:
        handle_apply:

    ClassMethods:
        get_op_support: Return a tuple of supported operator type name.
    """

    op: str = Field(description="An operator type.")

    @abstractmethod
    def apply(
        self,
        df: Any,
        engine: DictData,
        metric: MetricOperatorOrder,
        **kwargs,
    ) -> Any:
        """Apply operator transform abstraction method.

        Args:
            df (Any): An any DataFrame API instance.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperatorOrder): A metric transform that was set from
                handler step for passing custom metric data.
        """

    def handle_apply(
        self,
        df: Any,
        context: DictData,
        engine: DictData,
        **kwargs,
    ) -> Any:
        """Handle Apply sub-transform logic.

        Args:
            df (Any): An any DataFrame API instance.
            context: (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
        """
        logger.info(f"👷🔧 Handle Apply Operator: {self.op!r}")
        metric = MetricOperatorOrder(type="order", trans_op=self.op)
        context["metric_operator"].append(metric)
        try:
            return self.apply(df, engine=engine, **kwargs)
        finally:
            self.post_apply(engine=engine, **kwargs)
            metric.finish()

    @classmethod
    def get_op_support(cls) -> tuple[str, ...]:
        """Get the tuple of supported operator for this transform model.

        Raises:
            TypeError: If override type of this `op` field does not be Literal.

        Returns:
            tuple[str, ...]: A tuple of operator name that was supported for
                this transform model.
        """
        ant = cls.model_fields["op"].annotation
        if get_origin(ant) is Literal:
            return get_args(ant)
        raise TypeError(f"Does not support `op` override with type: {ant}")

    @staticmethod
    @abstractmethod
    def sync_schema(pre, post, metric, **kwargs) -> None: ...

    def post_apply(self, engine: DictData, **kwargs): ...


class BaseSink(BaseModel, ABC):
    """Base Sink abstract model."""

    type: str = Field(description="A sink type.")

    @abstractmethod
    def save(
        self,
        df: Any,
        engine: DictData,
        metric: MetricSink,
        **kwargs,
    ) -> tuple[Any, Shape]:
        """Save abstract method for this sink model.

        Args:
            df (Any): An Any DataFrame API.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricSink): A metric sink that was set from handler step
                for passing custom metric data.

        Returns:
            tuple[Any, Shape]: A pair of an any DataFrame API and its Shape
                model.
        """

    @abstractmethod
    def outlet(self) -> tuple[str, str]:
        """Return a pair of type and name of the outlet data for the event hub
        service for create data lineage together with the inlet of source.

        Returns:
            tuple[str, str]: A pair of type and this sink name.
        """

    @abstractmethod
    def dest(self) -> str:
        """Return destination value of this sink model."""

    def handle_save(
        self,
        df: Any,
        context: Context,
        engine: DictData,
        **kwargs,
    ) -> Any:
        """Handle save method with adding source metric to the execution
        context.

        Args:
            df (Any): An Any DataFrame API.
            context: (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.

        Returns:
            Any: An Any DataFrame API specific with implemented engine.
        """
        logger.info(f"👷🎯 Handle Sink: {self.type!r} ...")
        metric = MetricSink(
            type=self.type, outlet=self.outlet(), destination=self.dest()
        )
        context.update({"metric_sink": metric})
        try:
            df, shape = self.save(df, engine=engine, metric=metric, **kwargs)
            metric.write_row_count = shape.rows
            metric.write_column_count = shape.columns
            if "mode" in self.model_fields:
                # noinspection Pydantic
                metric.mode = self.mode
            return df
        finally:
            metric.finish()
