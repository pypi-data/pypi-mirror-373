"""@private
Nothing in this module is useful for customers to invoke directly, hide it from the docs.
"""

import os

from enpi_api.l2.types.log import LogLevel, LogLevelModel


def env_or_raise(key: str) -> str:
    value = os.environ.get(key)
    if not value or value.strip() == "":
        raise ValueError(f"{key} environment variable is not set")
    return value


def get_api_host() -> str:
    return os.environ.get("ENPI_API_HOST", "https://api.igx.bio/v1")


def get_mlflow_host() -> str:
    return os.environ.get("ENPI_MLFLOW_HOST", "https://igx.bio/mlflow/")


def get_api_key() -> str | None:
    return os.environ.get("ENPI_API_KEY")


def get_api_key_or_error() -> str:
    return env_or_raise("ENPI_API_KEY")


def get_event_host() -> str:
    return os.environ.get("ENPI_EVENT_HOST", "igx.bio")


def get_event_port() -> int:
    return int(os.environ.get("ENPI_EVENT_PORT", "443"))


def get_event_root_topic() -> str:
    # Allow to be overwritten for local development
    return os.environ.get("ENPI_EVENT_ROOT_TOPIC", get_event_host())


def get_log_level() -> LogLevel:
    if os.environ.get("VERBOSE"):
        return LogLevel.Trace
    else:
        return LogLevelModel.model_validate(dict(level=os.environ.get("LOG_LEVEL", "DEBUG").upper())).level
