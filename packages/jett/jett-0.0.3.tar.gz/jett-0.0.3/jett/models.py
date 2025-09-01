"""Base Model modules keep all necessary models that use for each engine,
metric, and convertor.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import model_validator
from typing_extensions import NotRequired, Self

from jett.__types import DictData
from jett.utils import get_dt_latest, get_dt_now


class Shape(BaseModel):
    """Shape model for keeping simple log for the Source and Sink metric model.

    Examples:
        Create Shape directly
        >>> Shape(rows=1, columns=2)

        Create Shape from_tuple classmethod.
        >>> Shape.from_tuple((1, 2))
    """

    rows: int = Field(default=0, ge=0, description="A row/record number.")
    columns: int = Field(default=0, ge=0, description="A column/field number.")

    @classmethod
    def from_tuple(cls, data: tuple[int, int]) -> Self:
        """Construct Shape model with a pair of rows and columns.

        Args:
            data: tuple[int, int]: A pair of rows and columns number.
        """
        rows, columns = data
        return cls(rows=rows, columns=columns)


class ColDetail(BaseModel):
    """A shared data structure of column detail that should be use only in
    Result model.

    Examples:
        >>> ColDetail(name="id", dtype="integer")
    """

    name: str = Field(description="A name of column.")
    dtype: str = Field(description="A data type of column in string format.")


class Result(BaseModel):
    """A shared data structure of result of Jett tool. This model will use to be
    an output from tool execution step.

    Examples:
        >>> Result(
        ...     data=[{"id": 1}, {"id": 2}],
        ...     columns=[ColDetail(name="id", dtype="integer")],
        ... )
    """

    data: list[Any] = Field(
        default_factory=list,
        description="A sample data that already save to the sink.",
    )
    columns: list[ColDetail] = Field(default_factory=list)
    schema_dict: dict[str, Any] = Field(default_factory=dict)


class EmitCond(str, Enum):
    """An Enum for Metric Emitter Condition."""

    ONLY_SUCCESS = "only_success"
    ONLY_FAILED = "only_failed"
    ALWAYS = "always"


ALWAYS = EmitCond.ALWAYS
ONLY_SUCCESS = EmitCond.ONLY_SUCCESS
ONLY_FAILED = EmitCond.ONLY_FAILED


Operation = Literal[">", ">=", "<", "<=", "=", "!="]


class BasicFilter(BaseModel):
    """A Configuration Model for Basic Filter."""

    col: str = Field(description="A column name.")
    op: Operation = Field(
        description=(
            "An operation type for filtering, an operator e.g. >, >=, <, <=, "
            "or =."
        )
    )
    value: str | None = Field(
        default=None,
        description="a value to be compared",
    )
    value_expression: str | None = Field(
        default=None,
        description="a value expression to be compared",
    )

    @model_validator(mode="after")
    def __validate_value_and_value_expression(self):
        """Validates value and value_expression should not be provided at the
        same time.
        """
        if (self.value is None) == (self.value_expression is None):
            raise ValueError(
                "Please choose either value or value_expression or specify one "
                "between value or value_expression."
            )
        return self

    def get_str_cond(self) -> str:
        """Get the string condition as a string from model."""
        return f"( {' '.join(self.get_cond())} )"

    def get_cond(self) -> tuple[str, str, str]:
        """Get order of condition."""
        return (
            (self.col, self.op, self.value_expression)
            if self.value_expression
            else (self.col, self.op, self.value)
        )


class BaseMetricData(BaseModel):
    """Base Metric class for any inheritance class of metric data.

    Methods:
        add: Add any custom data to the extra field.
    """

    extras: dict[str, Any] = Field(
        default_factory=dict,
        description="An extra metric data.",
    )
    start_dt: datetime = Field(
        default_factory=get_dt_now,
        description="A start datetime from start create this metric model.",
    )
    end_dt: datetime | None = Field(
        default=None,
        description="An end datetime from the handler method.",
    )
    latency_ms: float = Field(
        default=0,
        description="A latency from start to end.",
    )

    def add(self, key: str, value: Any) -> Self:
        """Add any custom data to the extras field by given a pair of key and
        value.

        Args:
            key (str): A key of this extras metric.
            value: A value of this extras metric.
        """
        self.__dict__["extras"][key] = value
        return self

    def finish(self) -> Self:
        """Set the end_dt field."""
        self.end_dt = get_dt_now()
        self.latency_ms = (self.end_dt - self.start_dt).total_seconds()
        return self


class MetricSource(BaseMetricData):
    """Metric Source model."""

    type: str | None = None
    read_row_count: int = 0
    read_column_count: int = 0
    inlet: tuple[str, str] | None = None


class MetricOperator(BaseMetricData):
    """Metric Operator model."""

    type: Literal["order"]
    trans_op: str


class MetricOperatorOrder(MetricOperator):
    """Metric Operator Transform order model."""

    transform_pre: dict[str, Any] = Field(default_factory=dict)
    transform_post: dict[str, Any] = Field(default_factory=dict)


class MetricOperatorGroup(BaseMetricData):
    """Metric Operator Transform group model."""

    type: Literal["group"]
    trans_op: Literal["group"] = "group"
    transforms: list[MetricOperator] = Field(default_factory=list)
    transform_pre: dict[str, Any] = Field(default_factory=dict)
    transform_post: dict[str, Any] = Field(default_factory=dict)


MetricOperatorTransform = Annotated[
    Union[
        MetricOperatorGroup,
        MetricOperatorOrder,
    ],
    Field(
        discriminator="type",
        description="A metric operator transform that dynamic with the `type`.",
    ),
]


class MetricTransform(BaseMetricData):
    transforms: list[MetricOperatorTransform] = Field(
        default_factory=list,
        description="List of transform operator metric.",
    )


class MetricSink(BaseMetricData):
    destination: str = ""
    write_row_count: int = 0
    write_column_count: int = 0
    outlet: tuple[str, str] | None = None
    type: str | None = None
    mode: str | None = Field(
        default=None,
        description="A sink mode that use like override or append",
    )


class MetricEngine(BaseMetricData):
    app_id: str | None = Field(
        default=None,
        description="An application ID that use on this engine session.",
    )
    type: str | None = Field(
        default=None,
        description="An engine type.",
    )


class MetricData(BaseModel):
    """A shared data structure of metric model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    run_result: bool = Field(
        default=False,
        description=(
            "A running result success to catch from execution if it true."
        ),
    )
    execution_time_ms: float = Field(
        default=0.0,
        description=(
            "An execution time that start when calling the execute method."
        ),
    )
    execution_start_time: datetime = Field(default_factory=get_dt_now)
    execution_end_time: datetime = Field(default_factory=get_dt_latest)
    exception: Exception | BaseException | None = None
    exception_name: str | None = None
    exception_traceback: str | None = None

    metric_engine: MetricEngine = Field(
        default_factory=MetricEngine,
        description="A metric engine that was created on the `handle_execute` method.",
    )
    metric_source: MetricSource = Field(default_factory=MetricSource)
    metric_transform: MetricTransform = Field(
        default_factory=MetricTransform,
        description="A metric transform that was created after `handle_apply` method.",
    )
    metric_sink: MetricSink = Field(default_factory=MetricSink)


class Context(TypedDict, total=False):
    """Context dict type for pre-validate for Jett tool execution."""

    # NOTE: Before execute
    author: str | None
    owner: str | None
    parent_dir: Path

    # NOTE: After execute
    run_result: NotRequired[bool]
    execution_time_ms: NotRequired[float]
    execution_start_time: NotRequired[datetime]
    execution_end_time: NotRequired[datetime]
    exception: NotRequired[Exception | BaseException]
    exception_name: NotRequired[str]
    exception_traceback: NotRequired[str]
    post_execution_output: NotRequired[Any]

    # NOTE: Updated from that layer.
    metric_engine: NotRequired[MetricEngine]
    metric_source: NotRequired[MetricSource]
    metric_sink: NotRequired[MetricSink]

    # NOTE: Not necessary keys for transform metric.
    metric_group_transform: NotRequired[Any]
    metric_operator: NotRequired[Any]

    metric_transform: NotRequired[MetricTransform]
    metric_extras: NotRequired[DictData]
