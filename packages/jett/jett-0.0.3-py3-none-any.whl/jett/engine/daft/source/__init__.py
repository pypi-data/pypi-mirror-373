from typing import Annotated, Union

from pydantic import Field

from .files.local import (
    LocalCsvFile,
    LocalJsonFile,
)

Source = Annotated[
    Union[
        LocalCsvFile,
        LocalJsonFile,
    ],
    Field(discriminator="file_format"),
]
