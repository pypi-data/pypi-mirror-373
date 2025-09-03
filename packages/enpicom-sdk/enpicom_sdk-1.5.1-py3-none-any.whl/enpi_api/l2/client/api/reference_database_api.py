from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.api_error import ApiErrorContext
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.reference_database import ReferenceDatabase, ReferenceDatabaseRevision


class ReferenceDatabaseApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_reference_databases(self) -> list[ReferenceDatabase]:
        """Get all available reference databases with all their revisions.

        Returns:
            list[enpi_api.l2.types.reference_database.ReferenceDatabase]: available reference databases with their revisions.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get all available reference databases.
            ```python
            with EnpiApiClient() as enpi_client:
                reference_databases = enpi_client.reference_database_api.get_reference_databases()
                print(reference_databases)
                print(reference_databases[0].revisions)
            ```
        """

        logger.info("Getting all available reference databases...")

        reference_db_api_instance = openapi_client.ReferenceDatabaseApi(self._inner_api_client)

        with ApiErrorContext():
            get_reference_dbs_response = reference_db_api_instance.get_reference_databases()

        logger.success(f"Successfully fetched {len(get_reference_dbs_response.reference_databases)} reference databases.")

        return [ReferenceDatabase.from_raw(reference_db) for reference_db in get_reference_dbs_response.reference_databases]

    def get_revision_by_name(
        self,
        name: str,
        species: str,
        label: str | None = None,
    ) -> ReferenceDatabaseRevision:
        """Get a single reference database revision by its name.

        Args:
            name (str): Name of a reference database.
            species (str): Name of the species linked to the reference database.
            label (str | None): Label of a reference database revision. If none is provided, the latest available revision will be fetched.

        Returns:
            enpi_api.l2.types.reference_database.ReferenceDatabaseRevision: A single reference database revision with reference database name included.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get the latest revision of "Reference A" reference database.
            ```python
            name = "Reference A"
            species = "Homo sapiens"

            # Label is an optional parameter - if it's missing, the latest revision version will be fetched
            label = None
            # label = "Version 1.0"

            revision = client.reference_database_api.get_revision_by_name(name, species, label)
            ```
        """

        logger.info(f"Getting revision with name: '{name}'...")

        reference_db_api_instance = openapi_client.ReferenceDatabaseApi(self._inner_api_client)

        payload = openapi_client.GetRevisionByNameBody(
            name=name,
            species=species,
            label=label,
        )

        with ApiErrorContext():
            get_revision_by_name_response = reference_db_api_instance.get_revision_by_name(payload)

        revision = get_revision_by_name_response.revision

        logger.success(f"Successfully fetched revision with name: '{revision.name}, {revision.label}' and ID: '{revision.reference_database_id}'.")

        return ReferenceDatabaseRevision.from_raw(revision)
