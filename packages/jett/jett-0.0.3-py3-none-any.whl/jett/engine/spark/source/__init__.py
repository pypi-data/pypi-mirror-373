from typing import Annotated, Union

from pydantic import Field

from .files.gcs import GCSCSVFile, GCSJsonFile
from .files.local import LocalCSVFile, LocalJsonFile
from .files.s3 import S3CSVFile, S3JsonFile
from .hive import Hive
from .jdbc import Jdbc, MySQL, Postgres
from .mongodb import MongoDB

LocalFile = Annotated[
    Union[
        LocalCSVFile,
        LocalJsonFile,
    ],
    Field(discriminator="file_format"),
]

S3File = Annotated[
    Union[
        S3CSVFile,
        S3JsonFile,
    ],
    Field(discriminator="file_format"),
]

GCSFile = Annotated[
    Union[
        GCSCSVFile,
        GCSJsonFile,
    ],
    Field(discriminator="file_format"),
]


Source = Annotated[
    Union[
        LocalFile,
        S3File,
        GCSFile,
        MongoDB,
        Postgres,
        MySQL,
        Jdbc,
        Hive,
    ],
    Field(
        discriminator="type",
        description="The source registry.",
    ),
]
