from __future__ import annotations

from pathlib import Path
from typing import Any, Union

DictData = dict[
    Union[str, int],  # NOTE: Key should be str or int
    Union[
        str, int, bool, float, list[Any], dict[Any, Any], Any
    ],  # NOTE: Value that catch from YAML parser.
]
StrOrPath = str | Path
StrOrNone = str | None
TupleStr = tuple[str, ...]
PairStr = tuple[str, str]
PrimitiveType = bool | float | int | str
