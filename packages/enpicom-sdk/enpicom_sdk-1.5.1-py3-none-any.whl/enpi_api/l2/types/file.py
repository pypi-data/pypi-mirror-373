from datetime import datetime
from enum import Enum
from typing import NewType

from enpi_api.l1 import openapi_client
from enpi_api.l2.tags import FileTags
from enpi_api.l2.types.tag import Tag
from enpi_api.l2.util.from_raw_model import FromRawModel

FileId = NewType("FileId", str)
"""The unique identifier of a file."""


class FileStatus(str, Enum):
    """Status of a file after upload."""

    PROCESSING = "processing"
    PROCESSED = "processed"


class File(FromRawModel[openapi_client.GetFilesSuccessResponseFilesInner]):
    """A single file."""

    id: FileId
    """Unique identifier of a file."""
    status: FileStatus
    """Status of a file after upload."""
    tags: list[Tag]
    """Set of tags assigned to a file."""

    @classmethod
    def _build(cls, raw: openapi_client.GetFilesSuccessResponseFilesInner) -> "File":
        return cls(
            id=FileId(raw.id),
            status=FileStatus(raw.status),
            tags=[Tag.from_raw(tag) for tag in raw.tags],
        )

    def name(self) -> str:
        """Get the name of the file.

        Returns:
            str: The name of the file.
        """

        [name_tag] = [tag for tag in self.tags if tag.id == FileTags.Filename]
        return str(name_tag.value)


class FederatedCredentials(FromRawModel[openapi_client.UploadFile200ResponseCredentials]):
    """A set of temporary federated credentials that allow file upload. Most likely needed only
    for `file_api` upload functions internal logic.
    @private
    """

    access_key_id: str
    """Access key ID of the temporary credentials."""
    access_key_secret: str
    """Secret access key of the temporary credentials."""
    session_token: str
    """Session token linked to the temporary credentials, required to
        be used together with the access keys."""
    expiration: datetime | None
    """Expiration date of the temporary credentials."""
    bucket: str
    """S3 bucket inside of which the uploaded file will be stored."""
    key: str
    """Location on the S3 bucket under which file will be stored."""

    @classmethod
    def _build(cls, raw: openapi_client.UploadFile200ResponseCredentials) -> "FederatedCredentials":
        return cls(
            access_key_id=raw.access_key_id,
            access_key_secret=raw.access_key_secret,
            session_token=raw.session_token,
            expiration=raw.expiration,
            bucket=raw.bucket,
            key=raw.key,
        )


class OnCollisionAction(str, Enum):
    """The action to take when uploading a file with the same name as an existing file."""

    OVERWRITE = "overwrite"
    SKIP = "skip"
    ERROR = "error"
