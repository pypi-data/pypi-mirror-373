from datetime import datetime
from typing import NewType

from enpi_api.l1 import openapi_client
from enpi_api.l2.util.from_raw_model import FromRawModel

ReferenceDatabaseId = NewType("ReferenceDatabaseId", str)
"""The unique identifier of a reference database."""
ReferenceDatabaseVersion = NewType("ReferenceDatabaseVersion", int)
"""Version of a reference database."""


class ReferenceDatabaseRevision(FromRawModel[openapi_client.ReferenceDatabaseRevisionWithName]):
    """A single reference database revision with reference database name and info included.

    Attributes:
        name (str): Name of a reference database.
        reference_database_id (ReferenceDatabaseId): Unique Identifier of a reference database.
        reference_database_version (ReferenceDatabaseVersion): Reference database revision version.
        label (str): Label of a reference database revision.
        public (bool): Determines if a reference database is visible and available to all users and organizations.
        species (str): Name of the species linked to a reference database.
        created_at (datetime): Date on which a reference database revision was created.
    """

    name: str
    """Name of a reference database."""
    reference_database_id: ReferenceDatabaseId
    """Unique Identifier of a reference database."""
    reference_database_version: ReferenceDatabaseVersion
    """Reference database revision version."""
    label: str
    """Label of a reference database revision."""
    public: bool
    """Determines if a reference database is visible and available to all users and organizations."""
    species: str
    """Name of the species linked to a reference database."""
    created_at: datetime
    """Date on which a reference database revision was created."""

    @classmethod
    def _build(cls, raw: openapi_client.ReferenceDatabaseRevisionWithName) -> "ReferenceDatabaseRevision":
        assert raw.created_at is not None

        return cls(
            name=str(raw.name),
            reference_database_id=ReferenceDatabaseId(str(raw.reference_database_id)),
            reference_database_version=ReferenceDatabaseVersion(int(raw.reference_database_version)),
            label=str(raw.label),
            public=bool(raw.public) if raw.public is not None else False,
            species=str(raw.species),
            created_at=raw.created_at,
        )

    @classmethod
    def from_raw_with_db(
        cls, raw: openapi_client.ReferenceDatabaseRevision, raw_reference_database: openapi_client.ReferenceDatabase
    ) -> "ReferenceDatabaseRevision":
        assert raw.created_at is not None

        return cls(
            name=str(raw_reference_database.name),
            reference_database_id=ReferenceDatabaseId(str(raw.reference_database_id)),
            reference_database_version=ReferenceDatabaseVersion(int(raw.reference_database_version)),
            label=str(raw.label),
            public=bool(raw_reference_database.public) if raw_reference_database.public is not None else False,
            species=str(raw_reference_database.species),
            created_at=raw.created_at,
        )


class ReferenceDatabase(FromRawModel[openapi_client.ReferenceDatabase]):
    """A single reference database with all it's revisions.

    Attributes:
        name (str): Name of a reference database.
        public (bool): Determines if a reference database is visible and available to all users and organizations.
        species (str): Name of the species linked to a reference database.
        created_at (datetime): Date on which a reference database revision was created.
        revisions (list[ReferenceDatabaseRevision]): A set of reference database revisions.
    """

    name: str
    """Name of a reference database."""
    public: bool
    """Determines if a reference database is visible and available to all users and organizations."""
    species: str
    """Name of the species linked to a reference database."""
    created_at: datetime
    """Date on which a reference database revision was created."""
    revisions: list[ReferenceDatabaseRevision]
    """A set of reference database revisions."""

    @classmethod
    def _build(cls, raw: openapi_client.ReferenceDatabase) -> "ReferenceDatabase":
        assert raw.created_at is not None

        return cls(
            name=str(raw.name),
            public=bool(raw.public or False),
            species=str(raw.species),
            created_at=raw.created_at,
            revisions=[ReferenceDatabaseRevision.from_raw_with_db(revision, raw) for revision in raw.revisions],
        )
