from __future__ import annotations

from typing import Annotated, Union

from pydantic import Field

from .arrow import Arrow
from .daft import Daft
from .dbt import Dbt
from .duckdb import DuckDB
from .polars import Polars
from .spark import Spark

Engine = Annotated[
    Union[
        Arrow,
        Daft,
        Polars,
        DuckDB,
        Spark,
        Dbt,
    ],
    Field(
        discriminator="type",
        description="The main engine registry models for operator model.",
    ),
]
