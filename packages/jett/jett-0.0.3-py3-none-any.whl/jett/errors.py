class BaseError(Exception):
    """Base Tool Exception class."""


class ToolError(BaseError):
    """Main Tool Exception class."""


class ToolValidationError(ToolError):
    """A Custom Exception raised when validation failed."""


class ToolTransformError(ToolError):
    """A Custom Exception raised when transform failed."""


class UtilError(Exception): ...


class CmdExecError(UtilError):  # pragma: no cov
    """Custom exception raised for command execution failures.

    This exception provides context about the failure, including the command's
    return code and any output from its standard error stream.
    """

    def __init__(self, message: str, return_code: int, stderr: str | None):
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr

    def __str__(self):
        message = super().__str__()
        if self.stderr:
            return (
                f"({self.return_code}): {message}\n--- Stderr ---\n"
                f"{self.stderr.strip()}"
            )
        return message
