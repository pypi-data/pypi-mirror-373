import os
import sys
from types import TracebackType
from typing import Self, Type

from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.client.api.basket_api import BasketApi
from enpi_api.l2.client.api.cluster_api import ClusterApi
from enpi_api.l2.client.api.collection_api import CollectionApi
from enpi_api.l2.client.api.enrichment_api import EnrichmentApi
from enpi_api.l2.client.api.file_api import FileApi
from enpi_api.l2.client.api.filter_api import FilterApi
from enpi_api.l2.client.api.liabilities_api import LiabilitiesApi
from enpi_api.l2.client.api.ml_api import MlApi
from enpi_api.l2.client.api.phylogeny_api import PhylogenyApi
from enpi_api.l2.client.api.reference_database_api import ReferenceDatabaseApi
from enpi_api.l2.client.api.sequence_annotation_api import SequenceAnnotationApi
from enpi_api.l2.client.api.tag_api import TagApi
from enpi_api.l2.client.api.whoami_api import WhoamiApi
from enpi_api.l2.client.api.workflow_api import WorkflowApi
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.util.client import get_configuration
from enpi_api.l2.util.env import env_or_raise, get_log_level


def configure_logger(level: LogLevel) -> None:
    """@private"""
    logger.remove()

    logger.add(
        sys.stdout,
        colorize=True,
        level=level,
    )


class EnpiApiClient:
    """The higher level API client to comfortably interact with the ENPICOM API.

    This class is a context manager, so it should be used with the `with` statement.

    By default, arguments are taken from the environment variables.

    Key is a required argument or the environment variable `ENPI_API_KEY` must be set.

    """

    _configuration: openapi_client.Configuration
    _log_level: LogLevel
    _extra_headers: dict[str, str] | None = None
    _inner_api_client: openapi_client.ApiClient

    basket_api: BasketApi
    cluster_api: ClusterApi
    collection_api: CollectionApi
    file_api: FileApi
    filter_api: FilterApi
    liabilities_api: LiabilitiesApi
    ml_api: MlApi
    sequence_annotation_api: SequenceAnnotationApi
    reference_database_api: ReferenceDatabaseApi
    tag_api: TagApi
    enrichment_api: EnrichmentApi
    phylogeny_api: PhylogenyApi
    whoami_api: WhoamiApi
    workflow_api: WorkflowApi

    def __init__(self, api_key: str | None = None, log_level: LogLevel = get_log_level()):
        """Initialize the API client.

        Args:
            api_key (str | None): The API key to use. If left blank the API key will be retrieved from the
                `ENPI_API_KEY` environment variable.
            log_level (LogLevel): The log level to use. Defaults to `DEBUG`.

        Raises:
            enpi_api.l2.client.enpi_api_client.ApiHostNotSet: When `ENPI_API_HOST` env variable is not set.
            enpi_api.l2.client.enpi_api_client.ApiKeyNotSet: When `ENPI_API_KEY` env variable is not set or passed as an argument.

        Example:

            ```python
            from enpi_api.l2.client.enpi_api_client import EnpiApiClient

            with EnpiApiClient() as enpi_client:
                # Use the client here, for example, access the collection api
                collection_api = enpi_client.collection_api
            ```
        """

        configure_logger(log_level)
        self._log_level = log_level
        self._configuration = get_configuration(api_key)

    def _add_extra_headers(self, headers: dict[str, str]) -> Self:
        self._extra_headers = headers if self._extra_headers is None else {**self._extra_headers, **headers}
        return self

    def __enter__(self) -> Self:
        self._inner_api_client = openapi_client.ApiClient(self._configuration)

        if os.environ.get("USER_ID") and os.environ.get("USER_ORG_ID") and os.environ.get("USER_DEFAULT_SPACE_ID"):
            self._add_extra_headers(
                {
                    env_or_raise("PUBLIC_API_USER_ID_HEADER"): str(os.environ.get("USER_ID")),
                    env_or_raise("PUBLIC_API_USER_ORG_HEADER"): str(os.environ.get("USER_ORG_ID")),
                    env_or_raise("PUBLIC_API_USER_DEFAULT_SPACE_HEADER"): str(os.environ.get("USER_DEFAULT_SPACE_ID")),
                }
            )

        if self._extra_headers:
            for header, value in self._extra_headers.items():
                logger.trace(f"Setting header {header} to {value}")
                self._inner_api_client.set_default_header(header, value)

        self.basket_api = BasketApi(self._inner_api_client, self._log_level)
        self.cluster_api = ClusterApi(self._inner_api_client, self._log_level)
        self.collection_api = CollectionApi(self._inner_api_client, self._log_level)
        self.file_api = FileApi(self._inner_api_client, self._log_level)
        self.filter_api = FilterApi(self._inner_api_client, self._log_level)
        self.liabilities_api = LiabilitiesApi(self._inner_api_client, self._log_level)
        self.ml_api = MlApi(self._inner_api_client, self._log_level)
        self.sequence_annotation_api = SequenceAnnotationApi(self._inner_api_client, self._log_level)
        self.reference_database_api = ReferenceDatabaseApi(self._inner_api_client, self._log_level)
        self.tag_api = TagApi(self._inner_api_client, self._log_level)
        self.enrichment_api = EnrichmentApi(self._inner_api_client, self._log_level)
        self.phylogeny_api = PhylogenyApi(self._inner_api_client, self._log_level)
        self.whoami_api = WhoamiApi(self._inner_api_client, self._log_level)
        self.workflow_api = WorkflowApi(self._inner_api_client, self._log_level)

        return self

    def __exit__(self, exc_type: Type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None) -> None:
        self._inner_api_client.__exit__(exc_type, exc, traceback)
