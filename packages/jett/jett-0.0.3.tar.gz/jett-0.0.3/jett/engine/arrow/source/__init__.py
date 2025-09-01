from typing import Annotated, Union

from pydantic import Field

from .files.local import (
    LocalCsvFileDataset,
    LocalCsvFileTable,
    LocalJsonFileTable,
    LocalParquetFileDataset,
)

LocalCsvFile = Annotated[
    Union[
        LocalCsvFileDataset,
        LocalCsvFileTable,
    ],
    Field(discriminator="arrow_type"),
]


Source = Annotated[
    Union[
        LocalCsvFile,
        LocalJsonFileTable,
        LocalParquetFileDataset,
    ],
    Field(discriminator="file_format"),
]
