from typing import Annotated, Union

from pydantic import Field

from .console import Console
from .files.local import LocalCSVFile

LocalFile = Annotated[
    Union[LocalCSVFile,],
    Field(discriminator="file_format"),
]

Sink = Annotated[
    Union[
        LocalFile,
        Console,
    ],
    Field(discriminator="type"),
]
