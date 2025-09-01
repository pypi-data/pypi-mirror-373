from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Final, Literal

from pydantic import Field, SecretStr
from pydantic.functional_validators import field_validator, model_validator

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

from ....__types import DictData
from ....models import BasicFilter, Shape
from ...__abc import BaseSource
from ..temp_storage import TempStorage

logger = logging.getLogger("jett")

ALLOWED_SSL_MODE: Final[tuple[str, ...]] = ("DISABLED", "PREFERRED", "REQUIRED")


class Jdbc(BaseSource):
    """JDBC Spark Source model."""

    type: Literal["jdbc"]
    protocol: str | None = None
    driver: str | None = None
    host: str = Field(description="A host URL for JDBC URI.")
    port: int | None = Field(
        default=None,
        description="A port number for JDBC URI.",
        ge=0,
    )
    username: str = Field(description="A username for JDBC URI.")
    password: SecretStr
    database: str
    table_name: str | None = None
    query: str | None = None
    properties: dict[str, str | int | bool] | None = None
    filter: list[BasicFilter] = Field(default_factory=list)
    sample_records: int | None = None
    fetch_size: int = Field(default=0, gt=0)
    query_timeout: int | None = 0
    partition_column: str | None = None
    lower_bound: int | str | None = None
    upper_bound: int | str | None = None
    num_partitions: int = Field(default=1)
    custom_schema: str | None = Field(None, alias="schema")
    allow_save_data_to_temp: bool = True
    lazy: bool = Field(default=True)

    @field_validator("database", "table_name", "partition_column")
    def __validate_space(cls, value: Any) -> Any:
        """Check field should not include space character."""
        if value and isinstance(value, str) and " " in value:
            raise ValueError("Cannot contain whitespace")
        return value

    @field_validator(*("lower_bound", "upper_bound"))
    def __check_boundary(cls, value: Any) -> Any:
        if value is None:
            return value

        if isinstance(value, str):
            try:
                datetime.fromisoformat(value)
                return value
            except ValueError:
                pass
        elif isinstance(value, int):
            return value

        raise ValueError(
            "field must be an integer, or an ISO format date/timestamp"
        )

    @model_validator(mode="after")
    def __post_validation(self):
        if (self.upper_bound is not None and self.lower_bound is None) or (
            self.upper_bound is None and self.lower_bound is not None
        ):
            raise ValueError("lower_bound or upper_bound is missing")

        if self.lower_bound is not None:
            _upper_bound = (
                self.upper_bound
                if isinstance(self.upper_bound, int)
                else datetime.fromisoformat(self.upper_bound)
            )
            _lower_bound = (
                self.lower_bound
                if isinstance(self.lower_bound, int)
                else datetime.fromisoformat(self.lower_bound)
            )
            if _upper_bound < _lower_bound:
                raise ValueError("upper bound must be greater than lower bound")

        if self.query is not None:
            if self.table_name is not None:
                raise ValueError(
                    "query and table_name cannot use at the same time"
                )
            elif self.partition_column is not None:
                raise ValueError(
                    "when query is set, partition_column is not allowed"
                )
        else:
            if self.table_name is None:
                raise ValueError("please supply either query or table_name")
        return self

    def get_tbl_or_query(self) -> dict[str, str]:
        target = {}
        if self.table_name is not None:
            target = {"dbtable": self.fullname()}
            logger.info(f"Source - table name: {self.fullname()}")
        elif self.query is not None:
            target = {"query": self.query}
            logger.info(f"Source - query: {self.query}")
        return target

    def get_uri(self) -> str:
        """Get JDBC connection uri."""
        uri = f"jdbc:{self.protocol}://{self.host}:{self.port}/{self.database}"
        if self.properties:
            parsed_properties = "&".join(
                [f"{k}={v}" for k, v in self.properties.items()]
            )
            uri = f"{uri}?{parsed_properties}"
        return uri

    def get_jdbc_options(self) -> dict[str, str]:
        """Get JDBC options."""
        uri: str = self.get_uri()
        options = {
            "driver": self.driver,
            "url": uri,
            "user": self.username,
            "password": self.password.get_secret_value(),
            "fetchSize": self.fetch_size,
            "queryTimeout": self.query_timeout,
        }
        logger.info(f"Source - uri: {uri}")
        logger.info(f"Source - username: {self.username}")
        logger.info(f"Source - JDBC driver name: {self.driver}")
        logger.info(f"fetch size: {self.fetch_size}")
        logger.info(f"query timeout: {self.query_timeout}")
        if self.custom_schema:
            options.update({"customSchema": self.custom_schema})
            logger.info(f"schema: {self.custom_schema}")
        return options

    def get_boundary(
        self, spark: SparkSession, options: dict[str, str]
    ) -> dict[str, str | int]:
        """Get the boundary if partition exists."""
        boundary_options = {"numPartitions": self.num_partitions}
        if self.partition_column is not None and self.num_partitions > 1:
            lower_bound = self.lower_bound
            upper_bound = self.upper_bound
            if (
                lower_bound is None
                and upper_bound is None
                and self.query is None
            ):
                logger.info(
                    "boundary not found. lower bound and upper bound will be "
                    "automatically updated."
                )
                tmp_options = options.copy()
                tmp_options["query"] = (
                    f"SELECT "
                    f"  MIN({self.partition_column}) "
                    f", MAX({self.partition_column}) "
                    f"FROM {self.fullname()}"
                )
                logger.info(f"query to find boundary: {tmp_options['query']}")
                lower_bound, upper_bound = (
                    spark.read.format("jdbc")
                    .options(**tmp_options)
                    .load()
                    .first()
                )

            boundary_options.update(
                {
                    "partitionColumn": self.partition_column,
                    "lowerBound": lower_bound,
                    "upperBound": upper_bound,
                }
            )

            logger.info(f"lower bound: {lower_bound}")
            logger.info(f"upper bound: {upper_bound}")
            logger.info(f"partition column: {self.partition_column}")
            logger.info(f"num partitions: {self.num_partitions}")

        return boundary_options

    def load(self, engine: DictData, **kwargs) -> tuple[DataFrame, Shape]:
        """Load JDBC to Spark DataFrame object.

        Args:
            engine (DictData): An engine context data that was created from the
                `post_execute` method. That will contain engine model, engine
                session object for this execution, or it can be specific config
                that was generated on that current execution.
        """
        spark: SparkSession = engine["spark"]
        options = self.get_jdbc_options()
        options: dict[str, str | int] = (
            options
            | self.get_boundary(spark, options=options)
            | self.get_tbl_or_query()
        )
        logger.info("load data from source via jdbc")
        df: DataFrame = spark.read.format("jdbc").options(**options).load()

        # NOTE: Apply filter.
        if self.filter:
            df = df.filter(" and ".join(f.get_str_cond() for f in self.filter))

        if self.sample_records:
            logger.info(f"Source - apply limit: {self.sample_records}")
            df = df.limit(self.sample_records)

        if not self.allow_save_data_to_temp:
            return df, Shape()

        temp_storage = TempStorage(spark, prefix=f"source__{self.type}")
        df = temp_storage.apply(df)
        rows: int = df.count()
        logger.info(f"Source - rows: {rows}")
        shape: tuple[int, int] = (rows, len(df.columns))
        engine["temp_storage"]["source"] = temp_storage
        return df, Shape.from_tuple(shape)

    def fullname(self):
        return self.table_name

    def inlet(self) -> tuple[str, str]:
        return self.type, self.fullname()


class Postgres(Jdbc):
    """Postgres Spark Source model."""

    type: Literal["postgresql"]
    protocol: str = "postgresql"
    driver: str = "org.postgresql.Driver"
    port: int = 5432
    schema_name: str = "public"

    def fullname(self) -> str:
        return f"{self.schema_name}.{self.table_name}"


class MySQL(Jdbc):
    """
    A Configuration Model for MySQL (Spark Engine)
    Implemented on top of BaseJDBCModel

    :param protocol: a protocol of MySQL
    :param driver: a driver name of MySQL
    :param port: port number
    """

    type: Literal["mysql"]
    protocol: Literal[
        "mysql",
        "mysql:loadbalance",
        "mysql:replication",
        "mysqlx",
        "mysql+srv",
        "mysql+srv:loadbalance",
        "mysql+srv:replication",
        "mysqlx+srv",
    ] = "mysql"
    driver: str = "com.mysql.cj.jdbc.Driver"
    port: int = 3306

    @field_validator("properties")
    def __validate_properties(cls, value: Any) -> Any:
        """Validate JDBC properties for MySQL data source."""
        if not isinstance(value, dict):
            return value

        for k, v in value.items():
            if isinstance(v, str) and v in ("True", "False"):
                value[k] = v.lower()
            if k == "sslMode" and v not in ALLOWED_SSL_MODE:
                raise ValueError(
                    f"sslMode {v} not allowed, support only {ALLOWED_SSL_MODE}"
                )
        return value

    def fullname(self) -> str:
        """Return the fullname of this MySQL data source."""
        return f"{self.database}.{self.table_name}"
