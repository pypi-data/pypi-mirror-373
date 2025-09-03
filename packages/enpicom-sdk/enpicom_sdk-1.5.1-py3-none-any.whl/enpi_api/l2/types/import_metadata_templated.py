from pydantic import BaseModel

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.tag import TagId


class Template(BaseModel):
    """A template entry for matching a tag based on a key in your metadata import in order to select
    results that should have a given annotation applied to."""

    key: str | None
    """The key (column) in your metadata from where the value will be taken to match your tag.

    When `None`, in case of matching a tag, it will use the tag's key. When matching an ID the names of the columns are
    the following:
        - `Unique Collection ID` when matching a collection ID
        - `Unique Clone ID` when matching a clone ID
        - `Unique Sequence ID` when matching a sequence ID
    """

    def to_api_payload_match_tag(self) -> openapi_client.TemplateValue:
        """@private"""
        return openapi_client.TemplateValue(type="template", key=self.key)

    def to_api_payload_match_id(self) -> openapi_client.TemplateValue:
        """@private"""
        return openapi_client.TemplateValue(type="template", key=self.key)


def template(key: str | None = None) -> Template:
    """Create a template entry for matching a tag based on a key in your metadata import.

    A convenience function to create a template entry that refers to a specific key in your metadata.

    Args:
        key (str | None): The key (column) in your metadata that will be used to match a tag. When `None`, in case
          of matching a tag, it will use the tag's key. When matching an ID the names of the columns are the following:
            - `Unique Collection ID` when matching a collection ID
            - `Unique Clone ID` when matching a clone ID
            - `Unique Sequence ID` when matching a sequence ID

    Returns:
        Template: A template entry instance.
    """
    return Template(key=key)


class TemplatedTag(BaseModel):
    """A templated tag entry to be used as annotation for the matched collections, clones or sequences in order to apply
    a new tag value into those results.

    Allows to refer to a specific key (column) in your metadata and use it to add a tag.
    """

    tag_id: TagId
    """The identifier of the tag that will be added or updated."""
    value: Template
    """The template specification that is used to refer to a specific key in your metadata."""

    def to_api_payload(self) -> openapi_client.TemplatedTagEntry:
        """@private"""
        return openapi_client.TemplatedTagEntry(id=self.tag_id, value=self.value.to_api_payload_match_tag())


def template_tag(tag_id: TagId, key: str | None = None) -> TemplatedTag:
    """Create a templated tag entry to annotate a collection, clone or sequence based on a key in your metadata.

    A convenience function to create a templated tag entry that refers to a specific key in your metadata.

    Args:
        tag_id (TagId): The identifier of the tag that will be added or updated.
        key (str | None): The key (column) in your metadata that will be used to add a tag. When `None`, falls back to
          the tag's key.

    Returns:
        TemplatedTag: A templated tag entry instance.
    """
    return TemplatedTag(tag_id=tag_id, value=template(key))


TemplatedTags = list[TemplatedTag]


class CollectionAnnotation(BaseModel):
    """Specify annotations on the collection level."""

    tags: TemplatedTags
    """The tags that you want to assign to the collection."""

    def to_api_payload(self) -> openapi_client.TemplatedSearchAndTagAnnotation:
        """@private"""
        return openapi_client.TemplatedSearchAndTagAnnotation(
            openapi_client.CollectionAnnotation(target="collection", tags=[tag.to_api_payload() for tag in self.tags])
        )


def collection_annotation(tags: TemplatedTags) -> CollectionAnnotation:
    """Specify annotations on the collection level.

    A convenience function to create a collection annotation instance.

    Args:
        tags (TemplatedTags): The tags that you want to assign to the collection.

    Returns:
        CollectionAnnotation: A collection annotation instance.
    """

    return CollectionAnnotation(tags=tags)


class CloneAnnotation(BaseModel):
    """Specify annotations on the clone level."""

    tags: TemplatedTags
    """The tags that you want to assign to the clone."""

    def to_api_payload(self) -> openapi_client.TemplatedSearchAndTagAnnotation:
        """@private"""
        return openapi_client.TemplatedSearchAndTagAnnotation(openapi_client.CloneAnnotation(target="clone", tags=[tag.to_api_payload() for tag in self.tags]))


def clone_annotation(tags: TemplatedTags) -> CloneAnnotation:
    """Specify annotations on the clone level.

    A convenience function to create a clone annotation instance.

    Args:
        tags (TemplatedTags): The tags that you want to assign to the clone.

    Returns:
        CloneAnnotation: A clone annotation instance.
    """
    return CloneAnnotation(tags=tags)


class SequenceAnnotation(BaseModel):
    """Specify annotations on the sequence level."""

    tags: TemplatedTags
    """The tags that you want to assign to the sequence."""

    def to_api_payload(self) -> openapi_client.TemplatedSearchAndTagAnnotation:
        """@private"""
        return openapi_client.TemplatedSearchAndTagAnnotation(
            openapi_client.SequenceAnnotation(target="sequence", tags=[tag.to_api_payload() for tag in self.tags])
        )


def sequence_annotation(tags: TemplatedTags) -> SequenceAnnotation:
    """Specify annotations on the sequence level.

    A convenience function to create a sequence annotation instance.

    Args:
        tags (TemplatedTags): The tags that you want to assign to the sequence.

    Returns:
        SequenceAnnotation: A sequence annotation instance.
    """
    return SequenceAnnotation(tags=tags)


Annotation = CollectionAnnotation | CloneAnnotation | SequenceAnnotation
"""Annotation (i.e. a group of templated tags) that can be added on a collection, clone or sequence level."""
