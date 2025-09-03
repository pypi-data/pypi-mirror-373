from enum import Enum
from typing import Mapping, NewType

from enpi_api.l1 import openapi_client
from enpi_api.l2.tags import CollectionTags
from enpi_api.l2.types.tag import Tag, TagId, TagKey, TagValue
from enpi_api.l2.util.from_raw_model import FromRawModel

CollectionId = NewType("CollectionId", int)
"""The unique identifier of a collection."""


class Receptor(str, Enum):
    """Receptor type."""

    IG = "ig"
    TR = "tr"
    UNKNOWN = "unknown"


class CollectionMetadata(FromRawModel[openapi_client.GetCollectionsSuccessResponseCollectionsInner]):
    """Collection metadata containing it's most important info. Metadata object does not
    contain sequence and clone data of given collection."""

    id: CollectionId
    """Unique identifier of a collection."""
    tags: list[Tag]
    """Set of collection level tags of a collection."""

    @classmethod
    def _build(cls, raw: openapi_client.GetCollectionsSuccessResponseCollectionsInner) -> "CollectionMetadata":
        return cls(
            id=CollectionId(int(raw.id)),
            tags=[Tag.from_raw(tag) for tag in raw.tags] if raw.tags is not None else [],
        )

    def name(self) -> str:
        """Get the name of the collection.

        Returns:
            str: The name of the collection
        """
        return str(self.get_tag_value(tag_id=CollectionTags.Name))

    def get_tag_value(self, tag_id: TagId) -> TagValue:
        """Get the value of the specified tag.

        Args:
            tag_id (TagId): The tag to get the value of.

        Returns:
            TagValue: The value of the tag.

        Raises:
            ValueError: If the tag does not exist.
        """
        tag = [t for t in self.tags if t.id == tag_id]
        if len(tag) == 0:
            raise ValueError(f"Tag {tag_id} does not exist")
        return tag[0].value


AdditionalImportMetadata = Mapping[TagKey, TagValue] | Mapping[TagId, TagValue]
"""Additional metadata that can be added to a collection."""
