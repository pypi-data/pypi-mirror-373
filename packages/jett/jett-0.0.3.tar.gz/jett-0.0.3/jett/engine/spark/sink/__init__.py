from typing import Annotated, Union

from pydantic import Field

from .console import Console
from .empty import Empty
from .iceberg.sink import Iceberg

Sink = Annotated[
    Union[
        Console,
        Empty,
        Iceberg,
    ],
    Field(discriminator="type"),
]
