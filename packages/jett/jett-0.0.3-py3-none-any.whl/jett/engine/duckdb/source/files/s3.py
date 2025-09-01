from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from duckdb import DuckDBPyRelation


from pydantic import Field

from .....__types import DictData
from .....models import Shape
from ....__abc import BaseSource


class S3CSVFile(BaseSource):
    """Local file data source."""

    type: Literal["s3"]
    file_format: Literal["csv"]
    path: str
    delimiter: str = "|"
    header: bool = Field(default=True)
    sample_records: int | None = 200

    def load(
        self, engine: DictData, **kwargs
    ) -> tuple["DuckDBPyRelation", Shape]:
        """Load CSV file to DuckDB Relation object."""
        import duckdb

        file_format: str = Path(self.path).suffix
        if file_format not in (".csv",):
            raise NotImplementedError(
                f"Local file format: {file_format!r} does not support for "
                f"loading with csv type."
            )
        cursor = duckdb.connect()
        cursor.execute(
            """
            INSTALL httpfs;
            LOAD httpfs;
            SET s3_region='us-east-1';
            SET s3_access_key_id='';
            SET s3_secret_access_key='';

            CREATE TABLE data AS SELECT CAST(started_at as DATE) as started_at_date, count(ride_id) as ride_id_count
            FROM read_csv_auto('s3://confessions-of-a-data-guy/*.csv')
            GROUP BY started_at_date;

            COPY data TO 's3://confessions-of-a-data-guy/ducky-results.parquet';
            """
        )
        df = cursor.sql("SELECT * FROM data")
        return df, Shape.from_tuple(df.shape)

    def inlet(self) -> tuple[str, str]:
        return "s3", self.path
