from loguru import logger
from pydantic import ValidationError

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.api_error import ApiErrorContext
from enpi_api.l2.types.filter import Condition, Filter, FilterId, TemplatedCondition, TemplatedFilter
from enpi_api.l2.types.log import LogLevel


class NameEmpty(Exception):
    """Thrown when the name of a filter is empty, which is not allowed."""

    def __init__(self) -> None:
        """@private"""
        super().__init__("Name cannot be empty")


class FilterApi:
    _inner_api_client: openapi_client.ApiClient
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def create_filter(self, name: str, condition: Condition, shared: bool = False) -> Filter:
        """Create a new filter.

        Args:
            name (str): The name of the filter.
            condition (enpi_api.l2.types.filter.Condition): The condition of the filter.
            shared (bool): Whether the filter should be shared with other users in the organization. Defaults to False.

        Returns:
            enpi_api.l2.types.filter.Filter: The newly created filter.

        Raises:
            enpi_api.l2.client.api.filter_api.NameEmpty: If the name of the filter is empty.
            enpi_api.l2.types.api_error.ApiError: If API request fails.
        """

        name = name.strip()
        if not name:
            raise NameEmpty()

        filter_api_instance = openapi_client.FilterApi(self._inner_api_client)

        # Since the filter could be either a normal or a templated one, we need to try both
        try:
            condition_as_json = condition.model_dump_json(indent=2)
            l1_condition = openapi_client.FilterCondition.from_json(condition_as_json)
        except (ValidationError, ValueError) as e:
            logger.error(f"Could not parse condition as either templated or normal filter condition: {e}")
            raise e

        create_filter_request = openapi_client.NewFilter(name=name, shared=shared, condition=l1_condition)

        with ApiErrorContext():
            create_filter_response = filter_api_instance.create_filter(create_filter_request)

        filter_id = FilterId(create_filter_response.id)

        logger.success(f"Created filter `{name}` with ID {filter_id}")

        return self.get_filter_by_id(filter_id=filter_id)

    def create_templated_filter(self, name: str, condition: TemplatedCondition, shared: bool = False) -> TemplatedFilter:
        """Create a new templated filter.

        Args:
            name (str): The name of the filter.
            condition (enpi_api.l2.types.filter.TemplatedCondition): The condition of the filter.
            shared (bool): Whether the filter should be shared with other people in the organization. Defaults to False.

        Returns:
            enpi_api.l2.types.filter.TemplatedFilter: The newly created filter.

        Raises:
            enpi_api.l2.client.api.filter_api.NameEmpty: If the name of the filter is empty.
            enpi_api.l2.types.api_error.ApiError: If API request fails.
        """

        name = name.strip()
        if not name:
            raise NameEmpty()

        filter_api_instance = openapi_client.FilterApi(self._inner_api_client)

        # Since the filter could be either a normal or a templated one, we need to try both
        try:
            condition_as_json = condition.model_dump_json(indent=2)
            l1_condition = openapi_client.TemplatedMetadataFilterCondition.from_json(condition_as_json)
        except (ValidationError, ValueError) as e:
            logger.error(f"Could not parse condition as either templated or normal filter condition: {e}")
            raise e

        create_filter_request = openapi_client.NewTemplatedFilter(name=name, shared=shared, condition=l1_condition)

        with ApiErrorContext():
            create_filter_response = filter_api_instance.create_templated_filter(create_filter_request)

        filter_id = FilterId(create_filter_response.id)

        logger.success(f"Created templated filter `{name}` with ID {filter_id}")

        return self.get_templated_filter_by_id(filter_id=filter_id)

    def get_filter_by_id(self, filter_id: FilterId) -> Filter:  # TODO: version parameter (when filter versioning is implemented)
        """Get a filter by its ID.

        Args:
            filter_id (enpi_api.l2.types.filter.FilterId): The ID of the filter to get.

        Returns:
            enpi_api.l2.types.filter.Filter: The filter with the given ID.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.
        """

        filter_api_instance = openapi_client.FilterApi(self._inner_api_client)

        with ApiErrorContext():
            get_filter_response = filter_api_instance.get_filter(filter_id=filter_id)

        return Filter.from_raw(get_filter_response)

    def get_templated_filter_by_id(self, filter_id: FilterId) -> TemplatedFilter:  # TODO: version parameter (when filter versioning is implemented)
        """Get a templated filter by its ID.

        Args:
            filter_id (enpi_api.l2.types.filter.FilterId): The ID of the filter to get.

        Returns:
            enpi_api.l2.types.filter.TemplatedFilter: The templated filter with the given ID.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.
        """

        filter_api_instance = openapi_client.FilterApi(self._inner_api_client)

        with ApiErrorContext():
            get_filter_response = filter_api_instance.get_templated_filter(filter_id=filter_id)

        return TemplatedFilter.from_raw(get_filter_response)
