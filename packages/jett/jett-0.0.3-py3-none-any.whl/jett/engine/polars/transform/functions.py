from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self

from ....__types import DictData
from ....errors import ToolTransformError
from ....models import MetricOperatorOrder
from ....utils import to_snake_case
from ...__abc import BaseEngine
from ..utils import col_path, extract_cols_without_array
from .__abc import BasePolarsTransform, ColMap

if TYPE_CHECKING:
    from polars import DataFrame
    from polars import Expr as Column

    PairCol = tuple[Column, str]

logger = logging.getLogger("jett")


class RenameSnakeCase(BasePolarsTransform):
    """Rename All columns to Snakecase operator transform model."""

    op: Literal["rename_snakecase"] = Field(
        description="An operator transform type.",
    )

    def apply(self, df: DataFrame, engine: DictData, **kwargs) -> DataFrame:
        """Apply to Rename Column with Snakecase to the Polars DataFrame.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
        """
        renames: dict[str, str] = {c: to_snake_case(c) for c in df.columns}
        logger.info(
            f"Start Rename All columns to Snakecase:\n"
            f"{json.dumps(renames, indent=1)}"
        )
        return df.rename(renames)


class RenameColumns(BasePolarsTransform):
    """Rename Columns Transform model."""

    op: Literal["rename"]
    columns: list[ColMap] = Field(description="A list of ColMap object.")
    allow_group_transform: bool = Field(default=False)

    def apply(self, df: DataFrame, engine: DictData, **kwargs) -> DataFrame:
        """Apply to Rename Column to the Polars DataFrame.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
        """
        logger.info(f"Rename columns statement:\n{self.columns}")
        return df.rename({col.source: col.name for col in self.columns})


class Expr(BasePolarsTransform):
    op: Literal["expr"]
    name: str
    query: str

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricOperatorOrder,
        **kwargs,
    ) -> PairCol:
        """Apply to Expr.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperatorOrder): A metric transform that was set from
                handler step for passing custom metric data.

        Returns:
            PairCol: A pair of Expr object and its alias name.
        """
        import polars as pl

        return pl.sql_expr(self.query), self.name


class Sql(BasePolarsTransform):
    op: Literal["sql"]
    sql: str | None = Field(default=None, description="A SQL statement.")
    sql_file: str | None = Field(
        default=None,
        description="A SQL file that want to load.",
    )

    @model_validator(mode="after")
    def __check_sql_and_sql_file(self) -> Self:
        """Check the necessary field of SQL use pass only SQL statement nor
        SQL filepath.
        """
        if not self.sql and not self.sql_file:
            raise ValueError("SQL and SQL file should not be empty together.")
        elif self.sql and self.sql_file:
            logger.warning(
                "If pass SQL statement and SQL file location together, it will "
                "use SQL statement first."
            )
        return self

    def apply(
        self,
        df: DataFrame,
        engine: DictData,
        metric: MetricOperatorOrder,
        **kwargs,
    ) -> DataFrame:
        """Apply to SQL query.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
            metric (MetricOperatorOrder): A metric transform that was set from
                handler step for passing custom metric data.

        Returns:
            DataFrame: A Polars DataFrame that have applied SQL query via `sql`
                method.
        """
        logger.info("Start Prepare SQL statement ...")
        if self.sql:
            sql: str = self.sql
        else:
            _engine: BaseEngine = engine["engine"]
            sql_file: Path = _engine.parent_dir / self.sql_file
            try:
                sql: str = sql_file.read_text()
            except FileNotFoundError:
                raise ToolTransformError(
                    f"SQL file does not exists {sql_file.resolve()}"
                ) from None
        logger.info(f"SQL Statement:\n{sql}")
        logger.info(f"{df.schema}")
        return df.sql(sql)


class SelectColumns(BasePolarsTransform):
    """Select Columns Operator transform model."""

    op: Literal["select"]
    columns: list[str]
    allow_missing: bool = Field(
        default=False,
        description=(
            "A flag to allow missing column when compare from the current "
            "DataFrame."
        ),
    )

    def apply(self, df: DataFrame, engine: DictData, **kwargs) -> DataFrame:
        """Apply to Select Column.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.

        Returns:
            DataFrame: A column selected Spark DataFrame.
        """
        selection: list[str] = self.columns
        if self.allow_missing:
            selection: list[str] = [c for c in self.columns if c in df.columns]
        return df.select(*selection)


class ExplodeArrayColumn(BasePolarsTransform):
    """Explode Array Column Operation transform model."""

    op: Literal["explode_array"]
    explode_col: str
    is_explode_outer: bool = True
    is_return_position: bool = False
    position_prefix_name: str = "_index_pos"

    def apply(self, df: DataFrame, engine: DictData, **kwargs) -> DataFrame:
        """Apply to Explode Array column.

        Args:
            df (DataFrame): A Polars DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.

        Returns:
            DataFrame: A Polars DataFrame that have exploded column.
        """
        import polars as pl

        if not self.is_return_position:
            logger.info("Start Explode Array Column")
            if self.is_explode_outer:
                return df.with_columns(pl.col(self.explode_col).explode())
            return df.with_columns(
                pl.col(self.explode_col).list.drop_nulls().explode()
            )
        raise NotImplementedError(
            "Does not support for return position column."
        )


class FlattenAllExceptArray(BasePolarsTransform):
    """Flatten all Columns except Array datatype Operator transform model."""

    op: Literal["flatten_all_except_array"]

    def apply(self, df: DataFrame, engine: DictData, **kwargs) -> DataFrame:
        """Apply to Flatten all Columns except Array or List data type.

        Args:
            df (Any): A Spark DataFrame.
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.

        Returns:
            DataFrame: A Polars DataFrame that already
        """
        selection: dict[str, Column] = {}
        for c in extract_cols_without_array(schema=df.schema):
            selection["_".join(c.split("."))] = col_path(c)

        logger.info("Start Flatten all columns except array")
        for k, v in selection.items():
            logger.info(f"> Target col: {k}, from: {v}")
        return df.with_columns(**selection).select(*selection.keys())
