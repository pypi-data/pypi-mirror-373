from typing import Annotated, Union

from pydantic import Field

from .console import Console
from .files.local import LocalCSVFile

Sink = Annotated[
    Union[
        LocalCSVFile,
        Console,
    ],
    Field(discriminator="type"),
]
