from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self

from ....__types import DictData
from ....errors import ToolTransformError
from ....utils import join_newline, to_snake_case
from ...__abc import BaseEngine
from .__abc import BaseDuckDBTransform
from .__models import ColumnMap

if TYPE_CHECKING:
    from duckdb import DuckDBPyRelation as Relation

logger = logging.getLogger("jett")


class Sql(BaseDuckDBTransform):
    """SQL Transform model."""

    op: Literal["sql"]
    alias: str = "df"
    sql: str | None = None
    sql_file: str | None = None
    allow_group_transform: bool = False

    @model_validator(mode="after")
    def __check_sql(self) -> Self:
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
        df: Relation,
        engine: DictData,
        **kwargs,
    ) -> Relation:
        """Apply to SQL Execution with priority transform.

        Args:
            df (Relation): A Relation instance.
            engine (DictData): Any submodule of BaseEngine.
        """
        import duckdb

        logger.info("Start SQL transform ...")
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
        logger.info(f"SQL Statement\n{sql}")
        return duckdb.sql(sql, alias="df")


class RenameSnakeCase(BaseDuckDBTransform):
    op: Literal["rename_snakecase"]
    allow_group_transform: bool = False

    def apply(self, df: Relation, engine: DictData, **kwargs) -> Relation:
        """Apply to Rename Columns to Snake case."""
        import duckdb

        old_cols = df.columns
        new_cols = [
            f'"{col_name}" AS {to_snake_case(col_name)}'
            for col_name in old_cols
        ]
        logger.info(f"Start convert to snakecase: \n{join_newline(new_cols)}")
        return duckdb.sql(f"SELECT {', '.join(new_cols)} FROM df")


class RenameColumns(BaseDuckDBTransform):
    """Rename Columns Transform model."""

    op: Literal["rename_columns"]
    columns: list[ColumnMap] = Field(description="A list of ColumnMap object.")
    allow_group_transform: bool = Field(default=False)

    def apply(self, df: Relation, engine: DictData, **kwargs) -> Relation:
        """Apply to Rename Column transform."""
        import duckdb

        stm: str = (
            f"SELECT * "
            f"RENAME ( {', '.join(c.gen_source() for c in self.columns)} ) "
            f"FROM df"
        )
        logger.info(f"Rename columns statement:\n{stm}")
        return duckdb.sql(query=stm, alias="df")


class DropColumns(BaseDuckDBTransform):
    op: Literal["drop_columns"]
    target_col: list[str]

    def apply(self, df: Relation, **kwargs) -> Relation: ...

    def apply_group(self, df: Relation, **kwargs) -> str: ...


class ExcludeColumns(BaseDuckDBTransform):
    """Exclude Columns"""

    op: Literal["exclude_columns"]
    columns: list[str]

    def apply(self, df: Relation, engine: DictData, **kwargs) -> Relation:
        """Apply to Exclude Columns"""
        import duckdb

        return duckdb.sql(
            f"SELECT * EXCLUDE ({', '.join(self.columns)}) FROM df"
        )
