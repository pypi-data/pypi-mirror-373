from __future__ import annotations

import copy
import re
from typing import TYPE_CHECKING, Final

from jett.utils import is_snake_case

if TYPE_CHECKING:
    from polars import Expr as Column
    from polars import Schema, Struct


ALLOW_VALIDATE_PATTERNS: Final[tuple[str, ...]] = (
    "non_snake_case",
    "whitespace",
)


def extract_col_with_pattern(
    schema: Schema | Struct,
    patterns: list[str],
    parent_cols: list[str] | None = None,
) -> list[str]:
    """Do recursive find the colum name that does not follow the pattern
    current supported patterns are non_snake_case and whitespace.

    Args:
        schema (Schema | Struct): A Schema or Struct Polars object.
        patterns (list[str]):
        parent_cols (list[str], default None):
    """
    from polars import Array, List, Struct

    parent_cols: list[str] = parent_cols or []

    def _validate_and_append_error(
        name: str,
        p_cols: list[str],
        e_cols: list[str],
        pt: list[str],
    ) -> list[str]:
        """Child Wrapped function for extract_pyspark_column_names_with_pattern
        validate snake case or whitespace and append error columns

        Args:
            name (str): A column name.
            p_cols: A parent columns
            e_cols: An error columns
            pt:
        """
        is_found_err: bool = False
        for pattern in pt:
            if pattern == "non_snake_case" and not is_snake_case(name):
                is_found_err = True
            elif pattern == "whitespace" and " " in name:
                is_found_err = True

        if is_found_err:
            e_cols.append(
                name if len(p_cols) == 0 else ".".join(p_cols) + f".{name}"
            )

        return e_cols

    if all(p not in ALLOW_VALIDATE_PATTERNS for p in patterns):
        raise ValueError(
            f"patterns must contain value in {ALLOW_VALIDATE_PATTERNS}"
        )

    error_cols: list[str] = []
    struct: Struct = (
        schema2struct(schema) if isinstance(schema, Schema) else Struct
    )
    for field in struct.fields:
        if isinstance(field.dtype, (Array, List)):
            if isinstance(field.dtype.inner, Struct):
                _parent_cols = copy.deepcopy(parent_cols)
                _parent_cols.append(field.name)
                error_cols = error_cols + extract_col_with_pattern(
                    schema=field.dtype.inner,
                    patterns=patterns,
                    parent_cols=_parent_cols,
                )
            else:
                error_cols: list[str] = _validate_and_append_error(
                    name=field.name,
                    p_cols=parent_cols,
                    e_cols=error_cols,
                    pt=patterns,
                )
        elif isinstance(field.dtype, Struct):
            _parent_cols = copy.deepcopy(parent_cols)
            _parent_cols.append(field.name)
            error_cols: list[str] = error_cols + extract_col_with_pattern(
                schema=field.dtype,
                patterns=patterns,
                parent_cols=_parent_cols,
            )
        else:
            error_cols: list[str] = _validate_and_append_error(
                name=field.name,
                p_cols=parent_cols,
                e_cols=error_cols,
                pt=patterns,
            )
    return error_cols


def validate_col_disallow_pattern(
    schema: Schema | Struct, patterns: list[str]
) -> None:
    """Validate columns names in dataframe (support nested schema) from the
    pattern.
    """
    if all(p not in ALLOW_VALIDATE_PATTERNS for p in patterns):
        raise ValueError(
            f"Patterns must contain value in {ALLOW_VALIDATE_PATTERNS}"
        )

    error_cols = extract_col_with_pattern(schema=schema, patterns=patterns)
    if len(error_cols) > 0:
        cols: str = ", ".join(error_cols)
        raise ValueError(
            f"Please check column naming convention (must not be {patterns!r}) "
            f"on columns: {cols}"
        )


def validate_col_allow_snake_case(schema: Schema | Struct) -> None:
    """Validate columns, allow only snake case."""
    validate_col_disallow_pattern(schema=schema, patterns=["non_snake_case"])


def schema2struct(schema: Schema) -> Struct:
    """Convert Schema object to Struct.

    Args:
        schema (Schema):

    Returns:
        Struct: A Struct object that create from the Polars Schema.
    """
    from polars import Field, Struct

    return Struct([Field(name, dtype) for name, dtype in schema.items()])


def extract_cols_selectable(
    schema: Schema | Struct, prefix: str = ""
) -> list[str]:
    """Extracts all selectable columns of given schema, support all top level
    column and nested column and array column.

    Args:
        schema (Schema | Struct): A Polars Schema object.
        prefix (str, default ''): A prefix value.

    Returns:
        list[str]: All cols like:
            ["c1", "c2.f1", "c2.f2", "c3"]

    Examples:
        Input:
        >>> from polars import Field, String, Int64, Float64
        >>> Struct(
        ...     [
        ...         Field("texts", List(String())),
        ...         Field("items", List(Struct(
        ...             [
        ...                 Field("name", String()),
        ...                 Field("price", Int64()),
        ...                 Field("detail", List(Struct(
        ...                     [
        ...                         Field("field1", String()),
        ...                         Field("field2", Float64()),
        ...                     ]
        ...                 )))
        ...             ]
        ...         )))
        ...     ]
        ... )

        Output:
        >>> [
        ...     'texts',
        ...     'texts[x]',
        ...     'items',
        ...     'items[x]',
        ...     'items[x].name',
        ...     'items[x].price',
        ...     'items[x].detail',
        ...     'items[x].detail[x]',
        ...     'items[x].detail[x].field1',
        ...     'items[x].detail[x].field2',
        ... ]
    """
    from polars import Array, List, Struct

    rs: list[str] = []
    struct: Struct = (
        schema2struct(schema) if isinstance(schema, Schema) else schema
    )
    for field in struct.fields:
        rs.append(prefix + field.name)
        if isinstance(field.dtype, Struct):
            rs.extend(
                extract_cols_selectable(field.dtype, f"{prefix}{field.name}.")
            )
        elif isinstance(field.dtype, (Array, List)):
            rs.append(f"{prefix}{field.name}[x]")
            if isinstance(field.dtype.inner, Struct):
                rs.extend(
                    extract_cols_selectable(
                        field.dtype.inner, f"{prefix}{field.name}[x]."
                    )
                )
    return rs


def extract_cols_without_array(schema: Schema) -> list[str]:
    """Extract selectable columns without array type.

        It returns only list of selectable columns that are not nested array
    type return only root array column name.

    Args:
        schema (Schema):

    Returns:
        list[str]: A list of column name that extract by selectable without
            array type.
    """
    selectable_cols: list[str] = extract_cols_selectable(schema=schema)
    nested_array_cols: list[str] = [c for c in selectable_cols if "[x]" in c]
    final_selectable_cols: list[str] = [
        c for c in selectable_cols if c not in nested_array_cols
    ]

    rs: list[str] = []
    for c in final_selectable_cols:
        is_not_parent_column: bool = True
        for fc in final_selectable_cols:
            if fc != c and fc.startswith(f"{c}."):
                is_not_parent_column: bool = False

        if is_not_parent_column:
            rs.append(c)
    return rs


def col_path(path: str) -> Column:
    """Convert a dotted path notation to polars column expression supports also
    list access

    Args:
        path (str): A column path.

    Examples:
        >>> col_path('a[5].b')

    References:
        - ISSUE - https://github.com/pola-rs/polars/issues/3123
        - FIX - https://gist.github.com/ophiry/78e6e04a8fde01e58ee289febf3bc4cc
    """
    import polars as pl

    parsed_path = re.findall(r"\.(\w+)|\[(\d+)]", f".{path}")
    expr: Column = pl.col(parsed_path[0][0])
    for field, index in parsed_path[1:]:
        if field:
            expr = expr.struct.field(field)
        elif index:
            expr = expr.list.get(int(index))
    return expr
