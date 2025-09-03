from typing import Sequence

from loguru import logger

from enpi_api.l1 import openapi_client
from enpi_api.l2.events.workflow_execution_task_waitable import WorkflowExecutionTaskWaitable
from enpi_api.l2.types.api_error import ApiError, ApiErrorContext
from enpi_api.l2.types.execution import Execution
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.tag import TagArchetype, TagDataType, TagLevel
from enpi_api.l2.types.task import TaskState
from enpi_api.l2.types.workflow import WorkflowExecutionId, WorkflowExecutionTaskId, WorkflowTaskTemplateName


class KeyEmpty(Exception):
    def __init__(self) -> None:
        """@private"""
        super().__init__("Key cannot be empty")


class TagLevelsEmpty(Exception):
    def __init__(self) -> None:
        """@private"""
        super().__init__("No tag `levels` provided, at least one level is needed.")


class CannotFilterCachedTags(Exception):
    def __init__(self) -> None:
        """@private"""
        super().__init__("Filtering cached tags (`cached=True`) by providing `keys` is not supported.")


class TagApi:
    _inner_api_client: openapi_client.ApiClient
    _cached_tag_archetypes: dict[TagLevel, list[TagArchetype]] = {}
    _log_level: LogLevel

    def __init__(self, inner_api_client: openapi_client.ApiClient, log_level: LogLevel):
        """@private"""
        self._inner_api_client = inner_api_client
        self._log_level = log_level

    def get_all_tag_archetypes(self, levels: Sequence[TagLevel] = ()) -> list[TagArchetype]:
        """Get all tag archetypes for the specified levels.

        Args:
            levels (Sequence[enpi_api.l2.types.tag.TagLevel]): The levels of the tags.

        Returns:
            list[enpi_api.l2.types.tag.TagArchetype]: The tag archetypes for the specified levels.

        Raises:
            enpi_api.l2.client.api.tag_api.TagLevelsEmpty: If no tag levels are provided.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            ```python
            levels = (TagLevel.COLLECTION, TagLevel.CLONE, TagLevel.SEQUENCE)
            all_tag_archetypes = client.tag_api.get_all_tag_archetypes(levels=levels)
            ```
        """
        if len(levels) == 0:
            raise TagLevelsEmpty()

        return [tag for level in levels for tag in self.get_tag_archetypes(level, cached=True)]

    def get_tag_archetypes(
        self,
        level: TagLevel,
        keys: list[str] | str | None = None,
        cached: bool = False,
    ) -> list[TagArchetype]:
        """Get tag archetypes for a specific level. Optionally filtered with keys.

        Args:
            level (enpi_api.l2.types.tag.TagLevel): The level of the tag. Defines the context in which the tag can be used.
            keys (list[str] | str | None): The key(s) of the tags to filter by. These will be matched
              case-insensitively and the key can be a partial match anywhere in the tag key.
            cached (bool): Whether to use cached tag archetypes. Defaults to False.

        Returns:
            list[enpi_api.l2.types.tag.TagArchetype]: The tag archetypes for the specified level.

        Raises:
            enpi_api.l2.client.api.tag_api.CannotFilterCachedTags: If `cached` is True and `keys` are provided at the same time, which is not supported.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Get all tag archetypes that have "nucleotides" or "amino acids" in their key
            ```python
            with EnpiApiClient() as enpi_client:
                nucleotide_and_amino_acid_tag_archetypes: List[TagArchetype] = enpi_client.tag_api.get_tag_archetypes(
                    level=TagLevel.SEQUENCE,
                    keys=["nucleotides", "amino acids"]
                )
            ```
        """

        # If keys is a string, convert it to a list
        if isinstance(keys, str):
            keys = [keys]

        if cached and keys is not None:
            raise CannotFilterCachedTags()

        if cached and level in TagApi._cached_tag_archetypes:
            return TagApi._cached_tag_archetypes[level]

        logger.info(f"Getting tag archetypes for level `{level.value}`")

        tag_api_instance = openapi_client.TagApi(self._inner_api_client)

        get_tags_request = openapi_client.GetTagsRequest(search=openapi_client.GetTagsRequestSearch(level=level.value, keys=keys))

        try:
            get_tags_response = tag_api_instance.get_tags(get_tags_request)
        except openapi_client.ApiException as e:
            raise ApiError(e)

        tag_archetypes = [TagArchetype.from_raw(tag) for tag in get_tags_response.tag_archetypes]

        if keys is None:
            TagApi._cached_tag_archetypes[level] = tag_archetypes

        return tag_archetypes

    def create_tag_archetype(self, level: TagLevel, data_type: TagDataType, key: str) -> Execution[TagArchetype]:
        """Create a new tag archetype.

        Args:
            level (enpi_api.l2.types.tag.TagLevel): The level of the tag. Defines the context in which the tag can be used.
            data_type (enpi_api.l2.types.tag.TagDataType): The data type of the tag.
            key (str): The display name of the tag. This must be unique in your organization.

        Returns:
            enpi_api.l2.types.execution.Execution[enpi_api.l2.types.tag.TagArchetype]: An awaitable that returns the created tag archetype.

        Raises:
            enpi_api.l2.client.api.tag_api.KeyEmpty: If the key is empty.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Create a new collection level tag with an integer data type
            ```python
            with EnpiApiClient() as enpi_client:
                created_tag_id: TagId = enpi_client.tag_api.create_tag_archetype(
                    level=TagLevel.COLLECTION,
                    data_type=TagDataType.INTEGER,
                    key="My custom integer tag"
                ).wait()
            ```
        """

        logger.info(f"Creating tag archetype `{key}` for level `{level.value}` with data type `{data_type.value}`")

        key = key.strip()
        if not key:
            raise KeyEmpty()

        tag_api_instance = openapi_client.TagApi(self._inner_api_client)
        payload = openapi_client.CreateTagRequest(tag=openapi_client.CreateTagRequestTag(key=key, data_type=data_type.value, level=level.value))

        with ApiErrorContext():
            create_tag_response = tag_api_instance.create_tag(payload)
            assert create_tag_response.workflow_execution_id is not None

            workflow_execution_id = WorkflowExecutionId(int(create_tag_response.workflow_execution_id))

            def on_complete(task_id: WorkflowExecutionTaskId, task_state: TaskState) -> TagArchetype:
                assert task_state == TaskState.SUCCEEDED, f"Task {task_id} did not reach {TaskState.SUCCEEDED} state, got {task_state} state instead"

                get_tag_id_response = tag_api_instance.get_tag_by_workflow_execution_task_id(task_id)
                tag_id = get_tag_id_response.tag_id
                assert tag_id is not None

                logger.success(f"Tag with ID `{tag_id}` was successfully created")

                # Get the tag we just created
                tag_archetypes = self.get_tag_archetypes(level, [key])
                tag_archetype = next(tag for tag in tag_archetypes if tag.id == tag_id)

                return tag_archetype

            waitable = WorkflowExecutionTaskWaitable[TagArchetype](
                workflow_execution_id=workflow_execution_id, task_template_name=WorkflowTaskTemplateName.ENPI_APP_TAG_CREATE, on_complete=on_complete
            )

            return Execution(wait=waitable.wait_and_return_result, check_execution_state=waitable.check_execution_state)

    def get_tag_archetype_by_name(self, level: TagLevel, key: str) -> TagArchetype | None:
        """Find a tag archetype by its name.

        Args:
            level (enpi_api.l2.types.tag.TagLevel): The level of the tag. Defines the context in which the tag can be used.
            key (str): The key of the tag archetype. This is matched case insensitively, as no two tags can have
                the same key.

        Returns:
            enpi_api.l2.types.tag.TagArchetype | None: The tag archetype with the specified key. Or None if no tag archetype is found.

        Raises:
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:

            Get the sequence level tag archetype with the key "My custom integer tag"
            ```python
            with EnpiApiClient() as enpi_client:
                tag_archetype: TagArchetype = enpi_client.tag_api.get_tag_archetype_by_name(TagLevel.Sequence, "My custom integer tag")
            ```
        """

        tag_archetypes = self.get_tag_archetypes(level, key)

        # Filter to key
        matches = [tag for tag in tag_archetypes if tag.key.lower() == key.lower()]

        match len(matches):
            case 0:
                return None
            case 1:
                tag_archetype = matches[0]
                return tag_archetype
            case _:
                raise ValueError(f"Multiple tag archetypes with key `{key}` found")

    def ensure_tag_archetype(self, level: TagLevel, data_type: TagDataType, key: str) -> Execution[TagArchetype]:
        """Ensure that a tag archetype exists. If it does not exist, create it.

        Args:
            level (enpi_api.l2.types.tag.TagLevel): The level of the tag. Defines the context in which the tag can be used.
            data_type (enpi_api.l2.types.tag.TagDataType): The data type of the tag.
            key (str): The display name of the tag. This must be unique in your organization.

        Returns:
            enpi_api.l2.types.execution.Execution[enpi_api.l2.types.tag.TagArchetype]: An awaitable that returns the created or existing tag archetype.

        Raises:
            enpi_api.l2.client.api.tag_api.KeyEmpty: If the key is empty.
            enpi_api.l2.types.api_error.ApiError: If API request fails.

        Example:
            Ensure that a collection level tag with the key "My custom integer tag" exists
            ```python
            with EnpiApiClient() as enpi_client:
                tag_archetype: TagArchetype = enpi_client.tag_api.ensure_tag_archetype(
                    level=TagLevel.COLLECTION,
                    data_type=TagDataType.INTEGER,
                    key="My custom integer tag"
                ).wait()
            ```
        """

        tag_archetype = self.get_tag_archetype_by_name(level, key)

        if tag_archetype is None:
            logger.debug("Creating new tag archetype")
            return self.create_tag_archetype(level, data_type, key)
        else:
            if tag_archetype.data_type != data_type:
                raise ValueError(f"Tag archetype `{key}` already exists with a different data type")

            logger.debug("Returning existing tag archetype")
            return Execution(wait=lambda: tag_archetype, check_execution_state=lambda: TaskState.SUCCEEDED)
