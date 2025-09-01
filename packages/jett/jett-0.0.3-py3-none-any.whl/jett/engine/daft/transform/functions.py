import logging
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from daft import DataFrame

from ....__types import DictData
from ....utils import to_snake_case
from .__abc import BaseDaftTransform

logger = logging.getLogger("jett")


class RenameSnakeCase(BaseDaftTransform):
    """Rename All Columns to Snakecase on the Arrow Table."""

    op: Literal["rename_snakecase"]

    def apply(self, df: "DataFrame", engine: DictData, **kwargs) -> "DataFrame":
        """Apply to Rename Columns to Snake case."""
        old_cols = df.column_names
        new_cols: dict[str, str] = {}
        logger.info("🔧 Start Apply Rename to Snakecase:")
        for c in old_cols:
            new_col: str = to_snake_case(c)
            logger.info(f"... {c!r} to {new_col!r}")
            new_cols[c] = new_col
        return df.with_columns_renamed(new_cols)
