from __future__ import annotations

import inspect
import math
import os
import random
import re
import shlex
import string
import subprocess
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from re import Pattern
from textwrap import dedent
from typing import Any, Final

import yaml

from jett.__types import DictData
from jett.errors import CmdExecError


def join_newline(value: list[str]) -> str:
    """Join the element in list of string with newline. This function use to
    avoid error when joining inside a format string syntax like
    `f\"{''.join(['foo', 'bar'])}\"`.

    Args:
        value: list[str]
    """
    return "\n".join(value)


def load_yaml(path: str | Path, add_info: bool = True) -> DictData:
    """Load YAML data. It will return empty data when the path does not exist.

    Args:
        path: A YAML filepath.
        add_info:

    Returns:
        DictData: return configuration data that extract from YAML file or
        return empty dict object if it does not exist.
    """
    path: Path = Path(path)
    if path.exists():
        file_state: os.stat = path.lstat()
        return (
            {
                "created_at": file_state.st_ctime,
                "updated_at": file_state.st_mtime,
                "parent_dir": path.parent,
            }
            if add_info
            else {}
        ) | yaml.safe_load(path.open(mode="r"))
    return {}


def write_yaml(path: str | Path, data: Any) -> None:
    """Write YAML file with an input data."""
    with open(path, mode="w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def get_dt_now() -> datetime:
    """Get the current datetime object with UTC timezone.

    Returns:
        datetime: The current datetime object with UTC timezone.
    """
    return datetime.now(timezone.utc)


def get_dt_latest() -> datetime:
    return datetime(9999, 12, 31)


def char_to_snake_case(name: str) -> str:
    """Converts a string to snake_case.

    Examples:
        - 'columnName'  -> 'column_name'
        - 'Column Name' -> 'column_name'
        - 'ColumnID'    -> 'column_id'
        - 'IDColumn'    -> 'id_column'
        - 'ID_Column_Name' -> 'id_column_name'
    """
    segments = name.split("_")
    converted_segments = []

    for segment in segments:
        if not segment:  # Handle multiple consecutive underscores
            continue

        # Apply camelCase/PascalCase conversion to each segment
        pattern: re.Pattern[str] = re.compile(
            r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+"
        )
        words: list[str] = pattern.findall(segment)
        if words:
            converted_segments.extend(w.lower() for w in words)

    return "_".join(converted_segments)


def to_snake_case(name: str) -> str:
    """Converts a string to snake_case, handling struct-like syntax.

    Examples:
        - 'columnName'  -> 'column_name'
        - 'Column Name' -> 'column_name'
        - 'ColumnID'    -> 'column_id'
        - 'IDColumn'    -> 'id_column'
        - 'struct<ACTUAL_TIMESTAMP:timestamp>' -> 'struct<actual_timestamp:timestamp>'
    """

    # NOTE: Handle struct-like syntax by processing field names within angle
    #   brackets
    def convert_struct_fields(match) -> str:
        struct_content = match.group(1)
        # Split by comma to handle individual fields
        fields = struct_content.split(",")
        converted_fields = []

        for field in fields:
            if ":" in field:
                # Split field name from type
                field_name, field_type = field.split(":", 1)
                # Convert only the field name to snake_case
                converted_name = char_to_snake_case(field_name.strip())
                converted_fields.append(f"{converted_name}:{field_type}")
            else:
                # No type specified, just convert the whole field
                converted_fields.append(char_to_snake_case(field.strip()))

        return f"struct<{','.join(converted_fields)}>"

    # NOTE: Check if this is a struct-like pattern
    struct_pattern = re.compile(r"struct<([^>]+)>")
    if struct_pattern.search(name):
        return struct_pattern.sub(convert_struct_fields, name)

    # NOTE: Use original logic for simple strings
    return char_to_snake_case(name)


def is_snake_case(input_str: str) -> bool:
    """Check that string is a snake case with number."""
    return bool(re.match(r"^[a-z0-9_]*$", input_str))


def is_optional(func: Callable, *, key: str) -> bool:
    signature = inspect.signature(func)
    for name, parameter in signature.parameters.items():
        if name == key:
            return parameter.kind == inspect.Parameter.KEYWORD_ONLY
    return False


is_optional_engine: partial[bool] = partial(is_optional, key="engine")


def bool2str(value: bool) -> str:
    """Convert boolean value to string value in (true or false)."""
    return "true" if value else "false"


def exec_command(
    cmd: str | list[str],
    encoding: str = "utf-8",
    **kwargs,
) -> subprocess.Popen[str]:
    """Execution command function that start to run subprocess built-in function
    and catch the stdout and stderr to return result.

    Args:
        cmd (str | list[str]): A command statement or list of command that want
            to execute with the subprocess.
        encoding (str, default "utf-8"): An encoding that use to parse std
            result.
    """
    if isinstance(cmd, str):
        args: list[str] = shlex.split(cmd)
    elif not isinstance(cmd, list) or not all(isinstance(c, str) for c in cmd):
        raise TypeError("The 'args' parameter must be a list of strings.")
    else:
        args: list[str] = cmd
    return subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding=encoding,
        errors="replace",  # Prevent UnicodeDecodeError from crashing the stream
        **kwargs,
    )


def handle_command(
    cmd: str | list[str],
    *,
    encoding: str = "utf-8",
    **kwargs,
) -> Iterator[str]:
    """Executes a command and yields its stdout line-by-line in real-time.

    This function is a generator that provides a secure and robust way to
    run an external command and process its output as a stream. It is designed
    to be resilient, handling errors such as the command not being found,
    permission issues, and non-zero exit codes from the command itself.

    Args:
        cmd: The command and its arguments as a list of strings. This is the
              only supported method for passing arguments to ensure security
              against command injection.
        encoding: The character encoding to use for decoding the subprocess's
                  stdout and stderr streams. Defaults to 'utf-8'.
        **kwargs: Additional keyword arguments to be passed directly to the
                  subprocess.Popen constructor.

    Yields:
        str: A line of output from the command's stdout, with leading/trailing
             whitespace removed.

    Raises:
        FileNotFoundError: If the command executable specified in `args`
           is not found in the system's PATH.
        PermissionError: If the script lacks the necessary permissions to
         execute the command.
        CmdExecutionError: If the command executes but returns a non-zero
           exit code, indicating a failure. The exception instance contains the
           return code and any captured stderr output.
        TypeError: If `args` is not a list of strings.
    """
    if isinstance(cmd, str):
        args: list[str] = shlex.split(cmd)
    elif not isinstance(cmd, list) or not all(isinstance(c, str) for c in cmd):
        raise TypeError("The 'args' parameter must be a list of strings.")
    else:
        args: list[str] = cmd

    proc: subprocess.Popen | None = None
    try:
        proc: subprocess.Popen = exec_command(args, encoding=encoding, **kwargs)

        # The 'iter(proc.stdout.readline, "")' pattern is a robust way to
        # read from a stream until it's closed. It avoids issues with
        # different line endings and is efficient.
        for line in iter(proc.stdout.readline, ""):
            yield line.strip()

        # After stdout is exhausted, wait for the process to terminate.
        # This is crucial to get the final return code.
        return_code = proc.wait()

        # Capture any remaining stderr output for context in case of an error.
        stderr_output = proc.stderr.read()

        if return_code != 0:
            # The command ran but failed. Raise a custom, informative exception.
            command_str = " ".join(map(shlex.quote, args))
            raise CmdExecError(
                f"Command '{command_str}' failed with return code {return_code}",
                return_code=return_code,
                stderr=stderr_output,
            )

    except FileNotFoundError:
        # Provide a more helpful error message for this common issue.
        raise FileNotFoundError(
            f"Command not found: '{args}'. Please ensure it is installed and "
            f"in your system's PATH."
        ) from None  # Suppress the original exception chain for a cleaner message
    except PermissionError:
        raise PermissionError(
            f"Permission denied to execute command: '{args}'."
        ) from None
    finally:
        # This block ensures that resources are cleaned up, even if the
        # generator is not fully consumed (e.g., the consumer breaks the loop).
        if proc:
            # If the process is still running (e.g., generator was closed early),
            # terminate it to prevent orphaned processes.
            if proc.poll() is None:
                try:
                    proc.terminate()  # Ask nicely first
                    proc.wait(timeout=2)  # Give it a moment to die
                except subprocess.TimeoutExpired:
                    proc.kill()  # Forcefully kill if it doesn't terminate
                    proc.wait()  # Reap the killed process

            # Explicitly close the file handles to release OS resources.
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()


def get_random_str(n: int = 10) -> str:
    """Get random string."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def get_random_str_unique(n: int = 10) -> str:
    return f"{get_random_str(n)}{get_dt_now():%Y%m%d%H%M%S}"


def sort_non_sensitive_str(value: list[str]) -> list[str]:
    """Sort list of string by ignoring special characters and case-sensitive."""
    pattern: Pattern[str] = re.compile(r"[^a-zA-Z0-9]")
    return sorted(value, key=lambda s: pattern.sub("", s).lower())


def dt2str(
    val: datetime,
    sep: str = " ",
    timespec: str = "microseconds",
    add_utc_suffix: bool = False,
) -> str:
    """Covert datetime object to str with format `%Y-%M-%d %H:%M:%S.%s`"""
    rs: str = val.isoformat(sep=sep, timespec=timespec)
    return f"{rs}Z" if add_utc_suffix else rs


def clean_string(text: str) -> str:
    """Remove indent, double whitespace, double newlines from string."""
    text = dedent(text)
    text = text.replace("  ", "")
    text = text.split("\n")
    text = list(filter(None, text))
    text = "\n".join(text)
    return text


def format_bytes_humanreadable(num_bytes: int) -> str:
    """Format bytes into human-readable format."""
    if num_bytes == 0:
        return "0 B"

    size_name: tuple[str, ...] = ("B", "KB", "MB", "GB", "TB", "PB")
    i: int = int(math.floor(math.log(num_bytes, 1024)))
    p: float = math.pow(1024, i)
    s = round(num_bytes / p, 2)
    return f"{s} {size_name[i]}"


def truncate_str_with_byte_limit(
    input_str: str, mode: str, max_bytes: int = 1048576
) -> str:
    """Truncate string with maximum size of string cannot greater than given
    maximum bytes support truncate from head or tail.

    Args:
        input_str (str):
        mode (str):
        max_bytes (int, default is 1048576 (1MB)):
    """

    if mode not in ["head", "tail"]:
        raise ValueError("mode must be head or tail")

    encoded_string = input_str.encode("utf-8")
    encoded_string = (
        encoded_string[:max_bytes]
        if mode == "head"
        else encoded_string[-max_bytes:]
    )
    truncated_string = encoded_string.decode("utf-8", "ignore")
    return truncated_string


def regex_by_group(text: str, regex: str, n: int = 0) -> str:
    """Find text with regex and get only first match
    if not found, return empty string
    """
    match = re.search(regex, text)
    if match:
        return match.group(n)
    return ""


def get_exception_group():  # pragma: no cov
    """Return the ExceptionGroup for compatibility with python < 3.11."""
    try:
        from builtins import ExceptionGroup

        return ExceptionGroup
    except ImportError:
        from exceptiongroup import ExceptionGroup

        return ExceptionGroup


def env(name: str, module: str, *, default: str | None) -> str | None:
    return os.getenv(f"JETT__{module.upper()}__{name}", default)


spark_env: partial[str | None] = partial(env, module="SPARK")
tool_env: partial[str] = partial(os.getenv, "JETT_ENV", default="test")

# NOTE: Compiled regex for environment variable substitution is more performant.
#   Syntax: ${{ ENV_VAR:default_value }} (default_value is optional)
ENV_VAR_MATCHER: Final[Pattern[str]] = re.compile(
    r"\$\{\{\s*(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\s*(?::\s*(?P<default>.*?))?\s*}}"
)


def substitute_env_vars(value: Any) -> Any:
    """Recursively traverses the data structure and substitutes environment
    variables.

    Args:
        value: The current value from the YAML data (can be dict, list, str, etc.).

    Returns:
        The value with environment variables substituted.

    Raises:
        KeyError: If an environment variable is not set and has no default.
    """
    if isinstance(value, dict):
        return {k: substitute_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [substitute_env_vars(item) for item in value]
    if isinstance(value, str):
        return replace_string_env_var(value)
    return value


def replace_string_env_var(value: str) -> str:
    """Performs the actual environment variable substitution in a string.

    Args:
        value: The string value to process.

    Returns:
        The string with the placeholder replaced by the environment variable's value.
    """
    match = ENV_VAR_MATCHER.match(value)
    if not match:
        return value

    var_name = match.group("name")
    default_value = match.group("default")

    # Use os.getenv for thread-safe access to environment variables
    env_value = os.getenv(var_name)
    if env_value is not None:
        return env_value
    if default_value is not None:
        return default_value

    raise KeyError(
        f"Configuration error: Environment variable '{var_name}' is not set "
        "and no default value was provided."
    )
