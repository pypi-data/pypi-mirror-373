from enum import Enum
from typing import NewType

from typing_extensions import assert_never

from enpi_api.l1 import openapi_client
from enpi_api.l2.util.from_raw_model import FromRawModel

TagId = NewType("TagId", int)
"""The unique identifier of a tag."""

TagKey = str
"""The display name of a tag."""

TagValue = bool | int | float | str
"""The value name of a tag."""


class TagLevel(str, Enum):
    """Resource level of a tag."""

    COLLECTION = "collection"
    CLONE = "clone"
    SEQUENCE = "sequence"
    FILE = "file"
    CLONE_CONTEXTUAL = "clone_contextual"


class TagDataType(str, Enum):
    """Data type of a tag."""

    AMINO_ACID_SEQUENCE = "amino_acid_sequence"
    NUCLEOTIDE_SEQUENCE = "nucleotide_sequence"
    QUALITY_SEQUENCE = "quality_sequence"
    BOOLEAN = "boolean"
    DECIMAL = "decimal"
    INTEGER = "integer"
    TEXT = "text"


class TagAccessType(str, Enum):
    """Access type of a tag."""

    MUTABLE = "mutable"
    MUTABLE_NON_DELETABLE = "mutable_non_deletable"
    IMMUTABLE = "immutable"


class TagArchetype(FromRawModel[openapi_client.GetTagsSuccessResponseTagArchetypesInner]):
    """Archetype (model, definition) of a tag."""

    id: TagId
    """The unique identifier of a tag."""
    key: TagKey
    """The display name of a tag."""
    level: TagLevel
    """Resource level of a tag."""
    data_type: TagDataType
    """Data type of a tag."""
    access_type: TagAccessType
    """Access type of a tag."""

    @classmethod
    def _build(cls, raw: openapi_client.GetTagsSuccessResponseTagArchetypesInner) -> "TagArchetype":
        assert raw.id is not None
        return cls(
            id=TagId(int(raw.id)), key=raw.key, level=TagLevel(raw.level), data_type=TagDataType(raw.data_type), access_type=TagAccessType(raw.access_type)
        )


class Tag(FromRawModel[openapi_client.TagsInner]):
    """A single tag with an ID and a value."""

    id: TagId
    """The unique identifier of a tag."""
    value: TagValue
    """The value name of a tag."""

    @classmethod
    def _build(cls, raw: openapi_client.TagsInner) -> "Tag":
        def get_tag_value(x: openapi_client.TagValue) -> TagValue:
            # It will never be None, then something weird failed with Pydantic
            if x.actual_instance is None:
                raise ValueError("Tag value is None")
            else:
                if isinstance(x.actual_instance, bool):
                    return x.actual_instance
                elif isinstance(x.actual_instance, int):
                    return x.actual_instance
                elif isinstance(x.actual_instance, float):
                    return x.actual_instance
                elif isinstance(x.actual_instance, str):
                    return x.actual_instance
                else:
                    assert_never(x.actual_instance)

        tag_value = get_tag_value(raw.value)

        assert raw.id is not None
        return cls(id=TagId(int(raw.id)), value=tag_value)
