from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic.functional_validators import field_validator, model_validator

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, DataFrameReader, SparkSession

from ....__types import DictData
from ....models import BasicFilter, Shape
from ...__abc import BaseSource
from ..temp_storage import TempStorage

logger = logging.getLogger("jett")


def pipe_load_all_struct_pipe_project():
    return {
        "$project": {
            "_id": 1,
            "raw_json_value": 1,
        }
    }


def pipe_load_all_struct_pipe_and_fields():
    return {"$addFields": {"raw_json_value": "$$ROOT"}}


def pipe_load_all_struct_schema():
    return {
        "fields": [
            {"metadata": {}, "name": "_id", "nullable": True, "type": "string"},
            {
                "metadata": {},
                "name": "raw_json_value",
                "nullable": True,
                "type": "string",
            },
        ],
        "type": "struct",
    }


class AllStructExtraColumn(BaseModel):
    """A Sub Configuration Model for Param load_all_struct_extra_cols of
    MongoDBModel.
    """

    col: str
    dtype: str


class MongoDB(BaseSource):
    """MongoDB Spark Source model."""

    type: Literal["mongodb"]
    protocol: Literal["mongodb", "mongodb+srv"] = "mongodb"
    host: str | list[str]
    port: int = 27017
    username: str
    password: SecretStr
    database: str
    table_name: str
    mongo_schema: dict | None = Field(None, alias="schema")
    sample_size: int = 100
    auth_source: str | None = None
    pipeline: list[dict] | None = None
    partitioner: dict | None = None
    filter: list[BasicFilter] | None = None
    sample_records: int | None = None
    load_all_struct: bool = False
    load_all_struct_extra_cols: list[AllStructExtraColumn] | None = None
    allow_save_data_to_temp: bool = True
    read_preference: str = "secondaryPreferred"
    direct_connection: bool = True

    @field_validator("database", "table_name")
    def __check_space(cls, value: Any) -> Any:
        """Validate whitespace"""
        if isinstance(value, str) and " " in value:
            raise ValueError("cannot contain whitespace")
        return value

    @field_validator("sample_records")
    def __check_range(cls, value: Any) -> Any:
        """Validate number of sample records."""
        if (
            value is not None
            and isinstance(value, int)
            and (value < 1 or value > 10000)
        ):
            raise ValueError("range is between 0 and 10000")
        return value

    @field_validator("pipeline")
    def __check_empty_mongo_pipeline(cls, value: Any) -> Any:
        """Check that mongodb pipeline cannot be empty list."""
        if value is not None and isinstance(value, list) and len(value) == 0:
            raise ValueError("pipeline cannot be empty list")
        return value

    @field_validator("load_all_struct_extra_cols")
    def __check_load_all_struct_only_first_level(cls, value: Any) -> Any:
        """Check the columns cannot contain nested column, must be first level
        column only.
        """
        if value is not None and isinstance(value, list):
            for c in value:
                if "." in c.col or "struct" in c.dtype:
                    raise ValueError(f"{c} is not first level column")
        return value

    @model_validator(mode="after")
    def __post_validate(self):
        if self.load_all_struct is True and self.pipeline is not None:
            raise ValueError("please choose either load_all_struct or pipeline")

        if isinstance(self.host, str):
            hosts = self.host.split(",")
            if len(hosts) > 1:
                self.host = hosts

        if self.direct_connection is True and isinstance(self.host, list):
            raise ValueError(
                "direct_connection not allow to be true in case multi hosts, "
                "please change direct_connection to false"
            )

        return self

    def get_uri(self) -> str:
        """Get mongodb connection uri."""
        password = self.password.get_secret_value()
        if isinstance(self.host, list):
            host = ",".join(self.host)  # for multiple endpoints
        else:
            host = f"{self.host}:{self.port}"  # for single endpoints
        uri = f"{self.protocol}://{self.username}:{password}@{host}"
        _params = []
        if self.auth_source:
            _params.append(f"authSource={self.auth_source}")
        if self.read_preference is not None:
            _params.append(f"readPreference={self.read_preference}")
        if self.direct_connection:
            _params.append(
                f"directConnection={str(self.direct_connection).lower()}"
            )

        if len(_params) > 0:
            _params = "&".join(_params)
            uri = f"{uri}/?{_params}"
        logger.info("mongo uri: %s", uri.replace(password, "******"))
        return uri

    def set_pipeline_load_all_struct(
        self,
    ) -> tuple[list[Any], dict[str, Any]] | tuple[None, None]:
        """Set mongodb pipeline and pyspark schema to load all struct."""
        if self.load_all_struct:
            logger.info("load all struct of records as json string")
            project: dict[str, Any] = pipe_load_all_struct_pipe_project()
            schema: dict[str, Any] = pipe_load_all_struct_schema()
            project_cols = project["$project"]
            columns = schema["fields"]
            if self.load_all_struct_extra_cols is not None:
                for c in self.load_all_struct_extra_cols:
                    project_cols[c.col] = 1
                    columns.append(
                        {
                            "metadata": {},
                            "name": c.col,
                            "nullable": True,
                            "type": c.dtype,
                        }
                    )

            project["$project"] = project_cols
            schema["fields"] = columns
            return [
                pipe_load_all_struct_pipe_and_fields(),
                project,
            ], schema
        return None, None

    def load(self, engine: DictData, **kwargs) -> tuple[Any, Shape]:
        """Load MongoDB Source"""
        from pyspark.sql.types import StructType

        pipeline, schema = self.set_pipeline_load_all_struct()
        spark: SparkSession = engine["spark"]
        uri: str = self.get_uri()

        reader: DataFrameReader = (
            spark.read.format("mongodb")
            .option("comment", "Tool Spark MongoDB Connector")
            .option("connection.uri", uri)
            .option("database", self.database)
            .option("collection", self.table_name)
            .option("sampleSize", self.sample_size)
        )

        _mongo_schema: dict[str, Any] = schema or self.mongo_schema
        if _mongo_schema:
            logger.info("apply schema")
            reader = reader.schema(StructType.fromJson(_mongo_schema))

        if self.partitioner:
            logger.info("apply mongo partitioner")
            for k, v in self.partitioner.items():
                logger.info(f"{k}={v}")
                reader = reader.option(k, v)

        _mongo_pipeline = pipeline or self.pipeline
        if _mongo_pipeline:
            logger.info(f"apply pipeline: {_mongo_pipeline}")
            reader = reader.option("aggregation.pipeline", self._pipeline)

        df: DataFrame = reader.load()

        # NOTE: Apply filter.
        if self.filter:
            df = df.filter(" and ".join(f.get_str_cond() for f in self.filter))

        if self.sample_records:
            logger.info(f"Source - apply limit: {self.sample_records}")
            df = df.limit(self.sample_records)

        if self.allow_save_data_to_temp:
            temp_storage = TempStorage(spark, prefix=f"source__{self.type}")
            df = temp_storage.apply(df)
            rows: int = df.count()
            logger.info(f"Source - rows: {rows}")
            shape: tuple[int, int] = (rows, len(df.columns))
            engine["temp_storage"]["source"] = temp_storage
            return df, Shape.from_tuple(shape)
        return df, Shape()

    def inlet(self) -> tuple[str, str]:
        return self.type, f"{self.database}.{self.table_name}"
