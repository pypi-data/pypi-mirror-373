from typing import Annotated, Union

from pydantic import Field

from .console import Console

Sink: type[Console] = Annotated[
    Union[Console,],
    Field(discriminator="type"),
]
