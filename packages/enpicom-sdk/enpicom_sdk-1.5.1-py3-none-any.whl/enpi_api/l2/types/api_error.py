from types import TracebackType
from typing import Self, Type, cast

from loguru import logger

from enpi_api.l1 import openapi_client


def _get_error_message(error: BaseException | None) -> str:
    """Extracts the error message from an error object.
    @private

    Automatically checks if there is a `message` attribute in the error object, and if not, attempts to extract the
    message from either the `data` -> `message` chain, or the `data` -> `actual_instance` -> `message` chain.

    Args:
        error (Any): The error object to extract the message from.

    Returns:
        str: The error message.
    """

    if error is None:
        logger.error("Could not extract error message from error object: {}", error)
        return "Unknown"

    if hasattr(error, "message"):
        return cast(str, error.message)  # pyright: ignore [reportAttributeAccessIssue]
    # If the error was from a request/response, we traverse `data` -> `message`
    elif hasattr(error, "data") and hasattr(error.data, "message"):  # pyright: ignore [reportAttributeAccessIssue]
        return cast(str, error.data.message)  # pyright: ignore [reportAttributeAccessIssue]
    # If the error was from a request/response, we traverse `data` -> `actual_instance` -> `message`
    # This case is for the Pydantic union types
    elif hasattr(error, "data") and hasattr(error.data, "actual_instance") and hasattr(error.data.actual_instance, "message"):  # pyright: ignore [reportAttributeAccessIssue]
        return cast(str, error.data.actual_instance.message)  # pyright: ignore [reportAttributeAccessIssue]
    else:
        # At least log it as fallback
        logger.error("Could not extract error message from error object: {}", error)
        return "Unknown"


class ApiError(Exception):
    """An error that is raised when an error occurred in the API.

    It attempts to retrieve the error message from the error object.
    """

    message: str
    """The error message of the API error."""
    error: BaseException | None
    """The error object that caused the API error."""

    def __init__(self, error: BaseException | None) -> None:
        """@private"""
        self.message = f"API error: {_get_error_message(error)}"
        self.error = error

    def __str__(self) -> str:
        return self.message


class ApiErrorContext:
    """Context manager for common API error handling

    Re-maps openapi_client.ApiException to ApiError

    Example:
        ```python
        with ApiErrorMapper():
            data = cluster_api_instance.get_cluster_runs()
        ```
    """

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None) -> None:
        if exc_type is openapi_client.ApiException:
            raise ApiError(exc)
