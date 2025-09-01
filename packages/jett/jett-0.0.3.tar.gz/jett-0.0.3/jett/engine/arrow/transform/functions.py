import logging
from typing import Literal

from pyarrow import Table

from ....__types import DictData
from ....utils import to_snake_case
from .__abc import BaseArrowTransform

logger = logging.getLogger("jett")


class RenameSnakeCase(BaseArrowTransform):
    """Rename All Columns to Snakecase on the Arrow Table."""

    op: Literal["rename_snakecase"]

    def apply(self, df: Table, engine: DictData, **kwargs) -> Table:
        """Apply to Rename Columns to Snake case."""
        old_cols = df.column_names
        new_cols: dict[str, str] = {}
        logger.info("🔧 Start Apply Rename to Snakecase:")
        for c in old_cols:
            new_col: str = to_snake_case(c)
            logger.info(f"... {c!r} to {new_col!r}")
            new_cols[c] = new_col
        return df.rename_columns(new_cols)
