from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame

    PairCol = tuple[Column, str]

from ..utils import (
    extract_cols_selectable,
    has_fix_array_index,
    replace_fix_array_index_with_x_index,
)

logger = logging.getLogger("jett")


class ColMap(BaseModel):
    """Column Map model."""

    name: str = Field(description="A new column name.")
    source: str = Field(
        description="A source column statement before alias with alias.",
    )
    dtype: str | None = Field(default=None, description="A data type")
    allow_quote: bool = True

    def get_null_pair(self) -> PairCol:
        """Create a new null column with specific data type.

        Returns:
            PairCol: A pair of Column instance and its alias name.
        """
        from pyspark.sql.functions import lit

        column: Column = lit(None)
        if self.dtype:
            column = column.cast(self.dtype)
        return column, self.name


class RenameColMap(ColMap):
    """Rename Column Map model. This model add useful methods that need to use
    for rename.
    """

    def get_rename_pair(self) -> PairCol:
        from pyspark.sql.functions import col, expr

        column: Column = (
            expr(self.source)
            if has_fix_array_index(self.source)
            else col(self.source)
        )
        if self.dtype:
            column = column.cast(self.dtype)

        return column, self.name

    def get_rename_pair_fix_non_existed_by_null(self, df: DataFrame) -> PairCol:
        _rename_cache_select_cols: list[str] | None = None
        if not _rename_cache_select_cols:
            _rename_cache_select_cols = extract_cols_selectable(df.schema)

        rep_from_col: str = self.source
        if has_fix_array_index(rep_from_col):
            rep_from_col = replace_fix_array_index_with_x_index(rep_from_col)

        if rep_from_col not in _rename_cache_select_cols:
            logger.info(
                f"Fill null on column: {self.name} (dtype {self.dtype}) due to "
                f"column {self.source} not found",
            )
            return self.get_null_pair()
        return self.get_rename_pair()
