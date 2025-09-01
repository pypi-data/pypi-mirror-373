from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

from pydantic.functional_validators import field_validator, model_validator

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

from ....__types import DictData
from ....models import BasicFilter, Shape
from ...__abc import BaseSource
from ..sql_parser import extract_table_names_from_query

logger = logging.getLogger("jett")


class Hive(BaseSource):
    """Hive Spark Source model."""

    type: Literal["hive", "iceberg"]
    database: str | None = None
    table_name: str | None = None
    query: str | None = None
    filter: list[BasicFilter] | None = None

    @field_validator("database", "table_name")
    def __validate_space(cls, value: Any) -> Any:
        if value is not None and isinstance(value, str) and " " in value:
            raise ValueError("cannot contain whitespace")
        return value

    @model_validator(mode="after")
    def __post_validate(self):
        if self.query:
            if self.database or self.table_name:
                raise ValueError(
                    "Cannot provide `query` and `db_name`/`table_name` at the "
                    "same time."
                )
        elif not self.database or not self.table_name:
            raise ValueError(
                "If `query` is not provided, both `db_name` and `table_name` "
                "must be specified."
            )

        return self

    def load(self, engine: DictData, **kwargs) -> tuple[Any, Shape]:
        spark: SparkSession = engine["spark"]
        if self.query:
            logger.info(f"loading source from: {self.query}")
            df = spark.sql(self.query)
        else:
            logger.info(
                f"loading source from: {self.database}.{self.table_name}",
            )
            spark.sql(f"use {self.database}")
            df = spark.table(self.table_name)

        if self.filter:
            df = df.filter(" and ".join(f.get_str_cond() for f in self.filter))

        if self.sample_records:
            logger.info(f"Source - apply limit: {self.sample_records}")
            df = df.limit(self.sample_records)

        rows: int = df.count()
        shape: tuple[int, int] = (rows, len(df.columns))
        return df, Shape.from_tuple(shape)

    def inlet(self) -> tuple[str, str]:
        if self.query:
            inlet_result = extract_table_names_from_query(self.query)
        else:
            inlet_result = f"{self.database}.{self.table_name}"
        return self.type, inlet_result
