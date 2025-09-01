from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any

from .utils import ENUM_EXTRACT_ARRAY_TYPE

if TYPE_CHECKING:
    from pyspark.sql.types import DataType, StructType

    Changed = dict[str, str | DataType | list[str]]
    ListStr = list[str]
    ListDictAny = list[dict[str, Any]]


def extract_struct_type(
    source_struct: DataType,
    table_struct: DataType,
    parent_cols: list[str] | None = None,
) -> list[Changed]:
    """A recursive function that walks into nested field of PySpark's Struct and
    collect the list of parent columns in each nested level, if the schema
    change found, it calls evaluate_schema_change() to evaluate the changes,
    otherwise, it has nested field.

    Args:
        source_struct: PySpark's schema of source DataFrame
        table_struct: PySpark's schema of table DataFrame
        parent_cols (list[str], default None): A list of parent columns of each
            nested fields

    Returns:
        list[Changed]
    """
    from pyspark.sql.types import ArrayType, StructType

    parent_cols: list[str] = parent_cols or []
    # NOTE: Found nested field or source struct is not the same data type
    #   as table struct e.g. array of string and array of struct.
    if (
        isinstance(source_struct, StructType)
        or source_struct.__class__ != table_struct.__class__
    ):
        return evaluate_schema_change(
            src_schema=source_struct,
            tgt_schema=table_struct,
            parent_cols=parent_cols,
        )

    if isinstance(source_struct, ArrayType):
        parent_cols.append(ENUM_EXTRACT_ARRAY_TYPE)
        return extract_struct_type(
            source_struct=source_struct.elementType,
            table_struct=table_struct.elementType,
            parent_cols=parent_cols,
        )
    return []


def evaluate_schema_change(
    src_schema: StructType,
    tgt_schema: StructType,
    parent_cols: list[str] | None = None,
) -> list[Changed]:
    """Evaluate the schema change (add, alter, and drop) between source schema
    and table schema in each field and nested field.

    Args:
        src_schema: PySpark's schema of source DataFrame
        tgt_schema: PySpark's schema of table DataFrame
        parent_cols: List of parent columns of each nested fields

    Returns:
        list[str]: list of schema changes, see structure of dict in list:
            Drop column
            >>> {
            ...     'type': 'drop_col',
            ...     'source_struct_type': StructField(),
            ...     'parent_cols': [],
            ... }

            Add column
            >>> {
            ...     'type': 'add_col',
            ...     'source_struct_type': StructField(),
            ...     'add_col_after': '',
            ...     'parent_cols': [],
            ... }

            Alter column
            >>> {
            ...     'type': 'alter_col',
            ...     'source_struct_type': StructField(),
            ...     'target_struct_type': StructField(),
            ...     'parent_cols': [],
            ... }
    """
    from pyspark.sql.types import ArrayType, StructField, StructType

    parent_cols: list[str] = parent_cols or []
    diffs: list[Changed] = []

    # NOTE: Handle case the source schema and table schema are not the same type.
    #   This case it will mark `Alter` type.
    if src_schema.__class__ != tgt_schema.__class__:
        diffs.append(
            {
                "type": "alter_col",
                "source_struct_type": src_schema,
                "target_struct_type": tgt_schema,
                "parent_cols": parent_cols,
            }
        )
        return diffs

    ### get to drop columns
    last_drop_col: str | None = None
    to_drop_cols: list[str] = []
    source_cols: list[str] = [s.name for s in src_schema]
    t: StructField
    for t in tgt_schema:
        if t.name not in source_cols:
            diffs.append(
                {
                    "type": "drop_col",
                    "source_struct_type": t,
                    "parent_cols": parent_cols,
                }
            )
            to_drop_cols.append(t.name)
            last_drop_col = t.name

    ### refresh the table schema
    tgt_schema: list[StructField] = [
        t for t in tgt_schema if t.name not in to_drop_cols
    ]

    ### Find new columns, column's data type change, and nested schema change
    nested_schema_changes: list[Changed] = []
    checked_table_cols: list[str] = []
    last_col_added = None
    _table_cols = [t.name for t in tgt_schema]

    for i, s in enumerate(src_schema):
        s: StructType | StructField
        for t in tgt_schema:
            if s.name == t.name:
                if s.dataType != t.dataType:
                    # NOTE: ignore s.nullable != t.nullable and
                    #   s.metadata != t.metadata.
                    if type(s.dataType) not in (StructType, ArrayType):
                        diffs.append(
                            {
                                "type": "alter_col",
                                "source_struct_type": s,
                                "target_struct_type": t,
                                "parent_cols": parent_cols,
                            }
                        )
                    else:
                        # nested schema is not equal
                        nested_schema_changes.append(
                            {
                                "type": "nested_schema_change",
                                "source_struct_type": s,
                                "table_struct_type": t,
                            }
                        )

                # always break if the column name is matched
                last_col_added = t.name
                checked_table_cols.append(t.name)
                break

            else:
                if s.name not in _table_cols and s.name not in [
                    d.get("source_struct_type").name for d in diffs
                ]:
                    # if first index, no add col after, set to None
                    _add_col_after = (
                        last_col_added
                        if (last_col_added or i == 0)
                        else last_drop_col
                    )
                    diffs.append(
                        {
                            "type": "add_col",
                            "source_struct_type": s,
                            "add_col_after": _add_col_after,
                            "parent_cols": parent_cols,
                        }
                    )
                    last_col_added = s.name

    # NOTE: Send all the nested schema change into a next level of struct
    for n in nested_schema_changes:
        _parent_cols: list[str] = copy.deepcopy(parent_cols)
        _parent_cols.append(n.get("table_struct_type").name)
        _func_out = extract_struct_type(
            source_struct=n.get("source_struct_type").dataType,
            table_struct=n.get("table_struct_type").dataType,
            parent_cols=_parent_cols,
        )
        diffs.extend(_func_out)

    return diffs


def clean_col_except_item_from_extract_array(
    columns: list[str] | str,
) -> list[str] | str:
    """Clean the list of columns or columns (str), remove the element (a flag
    from extracting array).
    """
    if not isinstance(columns, (list, str)):
        raise NotImplementedError("columns must be str or list of str only")

    is_str: bool = False
    if isinstance(columns, str):
        is_str: bool = True
        _cols: list[str] = columns.split(".")
    else:
        _cols = columns

    clean_columns = [c for c in _cols if c != ENUM_EXTRACT_ARRAY_TYPE]
    return ".".join(clean_columns) if is_str else clean_columns


def summarize_changes(
    changes: list[dict],
) -> tuple[ListDictAny, ListDictAny, ListDictAny]:
    """Get detail changes of alter columns, add columns, and drop columns"""
    alter_list: ListDictAny = []
    add_list: ListDictAny = []
    drop_list: ListDictAny = []
    for change in changes:
        change_type = change["type"]
        parent_cols = [
            col
            for col in change["parent_cols"]
            if col != ENUM_EXTRACT_ARRAY_TYPE
        ]
        share_dict = {
            "name": change["source_struct_type"].name,
            "data_type": change["source_struct_type"].dataType.simpleString(),
            "parent_cols": parent_cols,
        }
        match change_type:
            case "alter_col":
                alter_list.append(share_dict)
            case "add_col":
                add_list.append(share_dict)
            case "drop_col":
                drop_list.append(share_dict)

    return alter_list, add_list, drop_list
