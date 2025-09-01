from typing import Annotated, Union

from pydantic import Field

from .files.local import LocalCSVFile, LocalJsonFile

# LocalFile = Annotated[
#     Union[
#         LocalCSVFile,
#         LocalJsonFile,
#     ],
#     Field(discriminator="file_format"),
# ]

Source = Annotated[
    Union[
        LocalCSVFile,
        LocalJsonFile,
    ],
    Field(discriminator="file_format"),
]
