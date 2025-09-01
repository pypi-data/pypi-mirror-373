from typing import Annotated, Union

from pydantic import Field

from .functions import (
    DropColumns,
    ExcludeColumns,
    RenameColumns,
    RenameSnakeCase,
    Sql,
)

Transform = Annotated[
    Union[
        Sql,
        DropColumns,
        ExcludeColumns,
        RenameColumns,
        RenameSnakeCase,
    ],
    Field(discriminator="op"),
]
ListTransform = list[Transform]
