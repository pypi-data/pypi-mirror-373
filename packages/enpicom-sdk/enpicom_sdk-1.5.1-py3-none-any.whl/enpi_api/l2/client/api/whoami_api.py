from enpi_api.l1 import openapi_client
from enpi_api.l2.types.api_error import ApiError
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.whoami import Whoami


class WhoamiApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def whoami(self) -> Whoami:
        """Get information about the current key and who it is assigned to.

        Returns:
            enpi_api.l2.types.whoami.Whoami: Information about the current API key, and information about the user and
                organization it is assigned to.
        """
        whoami_api_instance = openapi_client.WhoamiApi(self._inner_api_client)

        try:
            response = whoami_api_instance.whoami()
        except openapi_client.ApiException as e:
            raise ApiError(e)

        return Whoami.from_raw(response)
