import datetime
import json
from collections.abc import Callable
from decimal import Decimal
from typing import Any

from pyspark.errors import PythonException
from pyspark.sql import Column, SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType


def clean_mongo_json_udf(
    spark: SparkSession,
    name: str | None = None,
) -> Callable[[Column | str], Column]:
    """Make the clean MongDB JSON string PySpark UDF.

    Args:
        spark (SparkSession): A Spark session.
        name (str, default None): A name for register `clean_mongo_json`
            function to the Spark session.

    Example:
        >>> from pyspark.sql.functions import col
        >>> clean_json_udf = clean_mongo_json_udf()
        >>> df = df.withColumn("clean_json", clean_json_udf(col("mongo_json")))
    """

    def clean_mongo_json(json_string: str) -> str:  # pragma: no cov
        """Clean MongoDB JSON string for PySpark UDF usage with SPARK-5063 support.

            Converts MongoDB extended JSON format to standard JSON by handling
        special MongoDB data types efficiently in a single optimized function.

        Supported MongoDB Data Types:
            - $oid → String (ObjectId)
            - $date → ISO datetime string
            - $numberLong → Integer
            - $numberDecimal → String (preserves precision)
            - $numberDouble → Float

        Args:
            json_string: MongoDB JSON string to clean

        Returns:
            Standard JSON string

        Raises:
            Exception: With detailed context for debugging
        """
        keys = frozenset(
            ["$oid", "$date", "$numberDecimal", "$numberDouble", "$numberLong"]
        )

        def parse_mongo_date(value: str | int | float) -> str:
            """Parse MongoDB date to ISO string."""
            if isinstance(value, str) and ("T" in value or "Z" in value):
                return datetime.datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                ).isoformat()

            # Handle numeric timestamp (milliseconds)
            timestamp = (
                float(value) / 1000.0
                if isinstance(value, str)
                else float(value) / 1000.0
            )
            return datetime.datetime.fromtimestamp(timestamp).isoformat()

        def parse_mongo_value(mongo_dict: dict) -> Any:
            """Convert MongoDB extended JSON value to standard type."""
            key, value = next(iter(mongo_dict.items()))
            parsers = {
                "$oid": str,
                "$date": parse_mongo_date,
                "$numberLong": int,
                "$numberDecimal": lambda v: str(Decimal(str(v))),
                "$numberDouble": float,
            }
            return parsers.get(key, lambda v: v)(value)

        def process_obj(obj: Any, path: str = "") -> Any:
            """Recursively process object, converting MongoDB types."""
            if isinstance(obj, dict):
                if not obj:
                    return {}

                # NOTE: Handle MongoDB special value (single key from keys)
                if len(obj) == 1 and next(iter(obj)) in keys:
                    try:
                        return parse_mongo_value(obj)
                    except Exception as err:
                        raise PythonException(
                            f"MongoDB value parsing failed at '{path}': {err}"
                        ) from err

                # NOTE: Process regular dict
                rs = {}
                for k, v in obj.items():
                    if v is not None:  # Skip null values
                        current_path = f"{path}.{k}" if path else k
                        rs[k] = process_obj(v, current_path)
                return rs

            elif isinstance(obj, list):
                return [
                    process_obj(item, f"{path}[{i}]")
                    for i, item in enumerate(obj)
                ]
            return obj

        try:
            if not json_string or not json_string.strip():
                return "{}"

            data = json.loads(json_string)
            result = process_obj(data)
            return json.dumps(result, separators=(",", ":"))

        except json.JSONDecodeError as e:
            preview = (
                json_string[:100] + "..."
                if len(json_string) > 100
                else json_string
            )
            raise PythonException(
                f"Invalid JSON: {e}. Input: '{preview}'"
            ) from e
        except Exception as e:
            if "MongoDB value parsing failed" in str(e):
                raise  # Re-raise parsing errors with context
            preview = (
                json_string[:50] + "..."
                if len(json_string) > 50
                else json_string
            )
            raise PythonException(
                f"Processing failed: {e}. Input: '{preview}'"
            ) from e

    spark.udf.register(
        name or "clean_mongo_json", clean_mongo_json, StringType()
    )
    return udf(lambda text: clean_mongo_json(text), StringType())
