from enum import Enum

from pydantic import BaseModel


class LogLevel(str, Enum):
    """Logging level setting for sdk's logs system."""

    Trace = "TRACE"
    Debug = "DEBUG"
    Info = "INFO"
    Success = "SUCCESS"
    Warning = "WARNING"
    Error = "ERROR"
    Critical = "CRITICAL"


class LogLevelModel(BaseModel):
    """Model for validating log level taken from an environment variable."""

    level: LogLevel
    """Validated log level setting."""
