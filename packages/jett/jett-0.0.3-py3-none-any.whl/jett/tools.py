from __future__ import annotations

import json
import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from typing import ClassVar, overload

from pydantic import BaseModel, Field, TypeAdapter, ValidationError
from typing_extensions import Self

from jett.__about__ import __version__
from jett.__types import DictData, StrOrPath
from jett.engine import Engine
from jett.errors import ToolError, ToolValidationError
from jett.models import Context, Result
from jett.utils import get_dt_now, load_yaml, substitute_env_vars, write_yaml

logger = logging.getLogger("jett")


class ToolModel(BaseModel):
    """Core Tool model that keep the parsing engine model and the original
    config data.

    Constructors:
        from_yaml: Construct Tool model with a YAML file path.
        from_dict: Construct Tool model with a dict object.

    Methods:
        fetch: Revalidate model from the current config data.
    """

    model: Engine = Field(
        description="A Tool model that already create on the registry module.",
    )
    data: DictData = Field(
        description="A configuration data that store with YAML template file."
    )
    extras: DictData = Field(
        default_factory=dict, description="An extra parameters."
    )
    created_at: datetime = Field(
        default_factory=get_dt_now,
        description=(
            "A created at of this config data if it load from YAML "
            "template file. It will use the current init time when this model "
            "created from dict."
        ),
    )

    @classmethod
    def from_yaml(
        cls,
        path: StrOrPath,
        *,
        extras: DictData | None = None,
    ) -> Self:
        """Construct Tool model with a YAML file path.

        Args:
            path (str | Path): A YAML path that want to load data.
            extras (DictData, default None): An extra parameters.
        """
        return cls.from_dict(load_yaml(path), extras=extras)

    @classmethod
    def from_dict(
        cls,
        data: DictData,
        *,
        extras: DictData | None = None,
    ) -> Self:
        """Construct Tool model with a dict object.

        Args:
            data (DictData): A dict value.
            extras (DictData, default None): An extra parameter.

        Raises:
            ToolValidationError: If model validation was failed.
        """
        try:
            _extras: DictData = extras or {}
            _data: DictData = data | _extras
            return cls.model_validate(
                {"model": _data, "data": _data, "extras": _extras}
            )
        except ValidationError as e:
            logger.exception(f"Create ToolModel from dict failed:\n\t{e}")
            raise ToolValidationError(e) from e

    def fetch(self, override: DictData | None = None) -> Self:
        """Recreate ToolModel `model` field with the current configuration data.

        Returns:
            Self: The new ToolModel instance with the current config data.
        """
        try:
            self.__dict__["model"] = TypeAdapter(Engine).validate_python(
                override or self.data
            )
        except ValidationError as e:
            logger.exception(f"Fetch model failed:\n\t{e}")
            raise ToolValidationError(e) from e


class Tool:
    """Tool object is tha main Python interface object for this
    package.

    Attributes:
        c (ToolModel): A Tool model that include the `model` and `data` fields.
        _path (str | Path, default None):
        _config (DictData, default None):

    Methods:
        refresh: Refresh the config argument with reload again from config path
            or config dict object.
    """

    @overload
    def __init__(self, *, path: StrOrPath) -> None:
        """Main construction with path of the YAML file."""

    @overload
    def __init__(self, *, config: DictData) -> None:
        """Main construction with dict of data."""

    def __init__(
        self,
        *,
        path: StrOrPath | None = None,
        config: DictData | None = None,
    ) -> None:
        """Main construction

        Args:
            path:
            config:

        Raises:
            ToolError: If path and config parameters was pass together.
            ToolError: If path and config be None value together.
        """

        # NOTE: Validate parameter with rule that should not supply both of its.
        if path and config:
            raise ToolError("Please pass only one for `path` nor `config`.")
        elif not path and not config:
            raise ToolError("Both of `path` and `config` must not be empty.")

        self._path: StrOrPath | None = path
        self._config: DictData | None = config
        # NOTE: Start pre-init.
        self.pre_init()

        self.c: ToolModel = (
            ToolModel.from_yaml(path) if path else ToolModel.from_dict(config)
        )

        # NOTE: Start post-init.
        self.post_init()

    def __str__(self) -> str:
        """Override the `__str__` dunder method."""
        return f"Tool Engine: {self.c.model.type}"

    def pre_init(self) -> None:
        """Pre initialize method for calling after this tool have initialed."""

    def post_init(self) -> None:
        """Post initialize method for calling after this tool have initialed."""

    def refresh(self) -> Self:
        """Refresh the config argument with reload again from config path or
        config dict object that pass from the initialize step.
        """
        self.c: ToolModel = (
            ToolModel.from_yaml(self._path)
            if self._path
            else ToolModel.from_dict(self._config)
        )
        return self

    def wrapped_execute(self, context: Context) -> Result:
        """Wrapped Execute with different use-case of tool that inherit this
        tool object.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.
        """
        # IMPORTANT: Recreate model before start handle execution.
        #   We replace env var template before execution for secrete value.
        logger.info(
            "🔐 Passing environment variables to the Tool config data and "
            "refresh ToolModel before execute."
        )
        self.c.fetch(override=substitute_env_vars(self.c.data))
        return self.c.model.handle_execute(context=context)

    def execute(
        self,
        *,
        allow_raise: bool = False,
    ) -> Result:
        """Execute the Tool operator with it model configuration.

        Args:
            allow_raise: bool
                If set be True, it will raise the error when execution was
                failed.

        Returns:
            Result: A Result object that already return from config engine
                execution result.
        """
        ts: float = time.monotonic()
        start_date: datetime = get_dt_now()
        context: Context = {
            "author": self.c.model.author,
            "owner": self.c.model.owner,
            "parent_dir": self.c.model.parent_dir,
        }
        rs: Result = Result()
        exception: Exception | None = None
        exception_name: str | None = None
        exception_traceback: str | None = None
        run_result: bool = True
        logger.info("Start Tool Execution:")
        logger.info(f"... 🚀 Tool Version: {__version__}")
        logger.info(f"... 👷 Author: {self.c.model.author}")
        logger.info(f"... 👨‍💻 Owner: {self.c.model.owner}")
        logger.info(f"... 🕒 Start: {start_date:%Y-%m-%d %H:%M:%S}")
        try:
            rs: Result = self.wrapped_execute(context=context)
            logger.info("✅ Execute successful!!!")
        except Exception as e:
            run_result = False
            exception = e
            exception_name = e.__class__.__name__
            exception_traceback = traceback.format_exc()
            logger.exception(f"😎👌🔥 Execution catch: {exception_name}")
        finally:
            # NOTE: Start prepare metric data after engine execution end. It
            #   will catch error exception class to this metric data if the
            #   execution raise an error.
            emit_context: Context = context | {
                "run_result": run_result,
                "execution_time_ms": time.monotonic() - ts,
                "execution_start_time": start_date,
                "execution_end_time": get_dt_now(),
                "exception": exception,
                "exception_name": exception_name,
                "exception_traceback": exception_traceback,
            }
            # NOTE: Raise the raised exception class if the raise flag allow
            #   from method parameter.
            if allow_raise and exception:
                logging.error(json.dumps(emit_context, default=str, indent=1))
                raise exception

            self.c.model.emit(context=emit_context)
        return rs

    def ui(self):
        """Generate UI for this valid Tool configuration data."""


class SparkSubmitTool(Tool):
    """Spark Submit Tool."""

    yaml_filename: ClassVar[str] = "tool_conf.yml"
    python_filename: ClassVar[str] = "tool_pyspark.py"
    python_code: ClassVar[str] = dedent(
        """
        from jett import Tool
        tool = Tool(path="{file}")
        tool.execute()
        """.lstrip(
            "\n"
        )
    )

    def post_init(self) -> None:
        """Post validate model type after create ToolModel that should to be the
        `spark` or `spark-submit` types
        """
        if self.c.model.type not in ("spark", "spark-submit"):
            raise ToolValidationError(
                f"Spark Submit Tool does not support for engine type: "
                f"{self.c.model.type!r}"
            )

        # NOTE: Force update type if it is `spark`.
        self.c.model.type = "spark-submit"
        self.c.data["type"] = "spark-submit"

    def set_conf_files(self, temp_path: Path) -> None:
        """Update Tool YAML filepath in the `spark-submit --files` command line
        statement.

        Args:
            temp_path (Path): A temp path.
        """
        file: str = f"file://{(temp_path / self.yaml_filename).absolute()}"
        logger.info(f"Add config files path: {file}")
        files = self.c.data.get("files", [])
        files.append(file)
        self.c.data["files"] = files

    def set_conf_entrypoint(self, temp_path: Path) -> None:
        """Write entrypoint of program and set entrypoint for spark-submit.

        Args:
            temp_path (Path): A temp path.
        """
        filepath = f"{temp_path}/{self.yaml_filename}"
        write_yaml(filepath, data=self.c.data)

        py_filepath = f"{temp_path}/{self.python_filename}"
        logger.info(f"pyspark entrypoint file path: {py_filepath}")

        # NOTE:
        #   - for spark-submit YARN cluster mode, file will be place in working
        #     directory
        #   - for local mode, it uses the temporary path created by Python
        #     Temporary directory
        config_filepath = self.yaml_filename
        if self.c.data.get("master", "").startswith("local"):
            config_filepath: str = py_filepath

        code: str = self.python_code.format(file=config_filepath)
        with open(py_filepath, mode="w", encoding="utf-8") as f:
            f.write(code)

        self.c.data["entrypoint"] = py_filepath
        self.c.data["type"] = "spark-submit"

    def wrapped_execute(self, context: Context) -> Result:
        """Wrapped Execute that will create temp-file before start Spark submit
        process.

        Args:
            context (Context): A execution context that was created from the
                core operator execution step this context will keep all operator
                metadata and metric data before emit them to metric config
                model.

        Returns:
            Result: An empty result object.
        """
        from .engine.spark import SparkSubmit

        with TemporaryDirectory(prefix="tool-") as tmp:
            temp_path: Path = Path(tmp)
            self.set_conf_files(temp_path)
            self.set_conf_entrypoint(temp_path)

            # IMPORTANT: Recreate model before start handle execution.
            #   We replace env var template before execution for secrete value.
            self.c.fetch(override=substitute_env_vars(self.c.data))

            model: SparkSubmit = SparkSubmit.model_validate(self.c.data)
            model.submit(context=context)

        return Result()


class DbtTool(Tool):
    """DBT Tool."""

    profile: ClassVar[str] = "./profile.yml"
    model_path: ClassVar[str] = "./dbt"


class RayTool(Tool):
    """Ray Tool."""


class GxTool(Tool):
    """Greate Expectation Tool."""
