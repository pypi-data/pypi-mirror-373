"""@private
Nothing in this module is useful for customers to invoke directly, hide it from the docs.
"""

from abc import abstractmethod
from typing import Generic, Self, TypeVar

from pydantic import BaseModel, PrivateAttr

RawType = TypeVar("RawType")


class FromRawModel(BaseModel, Generic[RawType]):
    """Base class for models that can be constructed from raw data.

    When we transform raw data from a response into a nicer model, we also want to store the raw data, just in case
    we forget to add a field to the model. That way users can always get the underlying raw results, just like they
    would if they were using the raw API.
    """

    _raw_data: RawType | None = PrivateAttr(None)
    """The raw data that was used to construct this object.

    We store this as a Pydantic private attribute, so it does not show up if you `print()` the model.
    """

    @classmethod
    def from_raw(cls, raw: RawType) -> Self:
        data = cls._build(raw)
        # Because it is a private attribute, we need to set it here, as it does not show up in the model's __init__.
        data._raw_data = raw
        return data

    @classmethod
    @abstractmethod
    def _build(cls, raw: RawType) -> Self:
        """Build the model from raw data.

        **DO NOT CALL THIS DIRECTLY.**

        This is called by `from_raw` to construct the entry, and then set the raw data attribute."""
        pass

    def raw(self) -> RawType:
        """Get the raw data that was used to construct this object.

        The raw data returned is exactly the same as it is when you would call the API endpoint directly.

        The raw data is only available if this was constructed from a response. If you create an object manually, this
        will raise a ValueError.
        """

        if self._raw_data is None:
            raise ValueError("This object was not constructed from a response")
        return self._raw_data
