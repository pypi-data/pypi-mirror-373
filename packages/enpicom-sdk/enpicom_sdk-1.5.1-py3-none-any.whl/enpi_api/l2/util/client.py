from enpi_api.l1 import openapi_client
from enpi_api.l2.util.env import get_api_host, get_api_key


class ApiHostNotSet(Exception):
    """Raised when `ENPI_API_HOST` is not set as an environment variable."""

    def __init__(self) -> None:
        """@private"""
        super().__init__("Must set either ENPI_API_HOST environment variable.")


class ApiKeyNotSet(Exception):
    """Raised when `ENPI_API_KEY` is not as an environment variable or passed as an argument to the client."""

    def __init__(self) -> None:
        """@private"""
        super().__init__("Must set either ENPI_API_KEY environment variable or pass it as an argument.")


def get_configuration(api_key: str | None = None) -> openapi_client.Configuration:
    host = get_api_host()
    if host is None:
        raise ApiHostNotSet()

    if api_key is None:
        api_key = get_api_key()
        if api_key is None:
            raise ApiKeyNotSet()
    return openapi_client.Configuration(host=host, api_key=dict(enpiApiKey=api_key))


def get_client(api_key: str | None = None) -> openapi_client.ApiClient:
    return openapi_client.ApiClient(get_configuration(api_key))
