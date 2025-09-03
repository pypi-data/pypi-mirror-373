from pydantic import BaseModel

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.tag import Tag


class CollectionAnnotation(BaseModel):
    """Specify annotations on the collection level."""

    tags: list[Tag]
    """The tags and values that you want to assign to the collection."""

    def to_api_payload(self) -> openapi_client.SearchAndTagAnnotation:
        return openapi_client.SearchAndTagAnnotation(
            openapi_client.CollectionAnnotation1(
                target="collection",
                tags=[
                    openapi_client.CollectionAnnotation1TagsInner(id=tag.id, value=openapi_client.CollectionAnnotation1TagsInnerValue(tag.value))
                    for tag in self.tags
                ],
            )
        )


class CloneAnnotation(BaseModel):
    """Specify annotations on the clone level."""

    tags: list[Tag]
    """The tags and values that you want to assign to the clone."""

    def to_api_payload(self) -> openapi_client.SearchAndTagAnnotation:
        return openapi_client.SearchAndTagAnnotation(
            openapi_client.CloneAnnotation1(
                target="clone",
                tags=[
                    openapi_client.CollectionAnnotation1TagsInner(id=tag.id, value=openapi_client.CollectionAnnotation1TagsInnerValue(tag.value))
                    for tag in self.tags
                ],
            )
        )


class SequenceAnnotation(BaseModel):
    """Specify annotations on the sequence level."""

    tags: list[Tag]
    """The tags and values that you want to assign to the sequence."""

    def to_api_payload(self) -> openapi_client.SearchAndTagAnnotation:
        return openapi_client.SearchAndTagAnnotation(
            openapi_client.SequenceAnnotation1(
                target="sequence",
                tags=[
                    openapi_client.CollectionAnnotation1TagsInner(id=tag.id, value=openapi_client.CollectionAnnotation1TagsInnerValue(tag.value))
                    for tag in self.tags
                ],
            )
        )


Annotation = CollectionAnnotation | CloneAnnotation | SequenceAnnotation
"""Annotation (i.e. a group of tags) that can be added on a collection, clone or sequence level."""
