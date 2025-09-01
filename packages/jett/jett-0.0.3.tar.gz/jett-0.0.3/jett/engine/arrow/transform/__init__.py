from typing import Annotated, Union

from pydantic import Field

from .functions import (
    RenameSnakeCase,
)

Transform = Annotated[
    Union[RenameSnakeCase,],
    Field(discriminator="op"),
]
