from enpi_api.l1 import openapi_client
from enpi_api.l2.types.organization import OrganizationId
from enpi_api.l2.types.user import UserId
from enpi_api.l2.util.from_raw_model import FromRawModel


class WhoamiKey(FromRawModel[openapi_client.Key]):
    """Information about the API key."""

    label: str
    """A descriptive label assigned to the API key."""

    @classmethod
    def _build(cls, raw: openapi_client.Key) -> "WhoamiKey":
        return cls(label=raw.label)


class WhoamiOrganization(FromRawModel[openapi_client.Organization]):
    """Information about the organization assigned to the API key."""

    id: OrganizationId
    """The unique identifier of the organization assigned to the API key."""

    @classmethod
    def _build(cls, raw: openapi_client.Organization) -> "WhoamiOrganization":
        assert raw.id is not None
        return cls(id=OrganizationId(int(raw.id)))


class WhoamiSpace(FromRawModel[openapi_client.SpacesInner]):
    """Information about a space that can be accessed with the API key."""

    id: int
    """The unique identifier of the space."""

    @classmethod
    def _build(cls, raw: openapi_client.SpacesInner) -> "WhoamiSpace":
        assert raw.id is not None
        return cls(id=raw.id)


WhoamiSpaces = list[WhoamiSpace]


class WhoamiUser(FromRawModel[openapi_client.User]):
    """Information about the user assigned to the API key."""

    id: UserId
    """The unique identifier of the user assigned to the API key."""
    is_machine: bool
    """Indicates whether the user is a real user or a machine user without a login."""

    @classmethod
    def _build(cls, raw: openapi_client.User) -> "WhoamiUser":
        assert raw.id is not None
        return cls(id=UserId(int(raw.id)), is_machine=raw.is_machine)


class Whoami(FromRawModel[openapi_client.Whoami]):
    """Information about the current user and organization assigned to the used API key."""

    key: WhoamiKey
    """Information about the API key."""
    organization: WhoamiOrganization
    """The organization assigned to this API key."""
    spaces: WhoamiSpaces
    """The spaces that can be accessed with this API key."""
    user: WhoamiUser
    """The user assigned to this API key."""

    @classmethod
    def _build(cls, raw: openapi_client.Whoami) -> "Whoami":
        return cls(
            key=WhoamiKey.from_raw(raw.key),
            organization=WhoamiOrganization.from_raw(raw.organization),
            spaces=[WhoamiSpace.from_raw(space) for space in raw.spaces],
            user=WhoamiUser.from_raw(raw.user),
        )
