"""@private
Nothing in this module is useful for customers to invoke directly, hide it from the docs.
"""

from typing import Sequence

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.tag import Tag


def tags_to_api_payload(tags: Sequence[Tag] = ()) -> list[openapi_client.TagsInner]:
    """Transform a list of Tag objects into the API payload types.
    @private

    Args:
        tags (Sequence[Tag]): A list of Tag objects.

    Returns:
        list[openapi_client.TagsInner]: A list of API payload types.
    """
    return [openapi_client.TagsInner(id=tag.id, value=openapi_client.TagValue(tag.value)) for tag in tags]
