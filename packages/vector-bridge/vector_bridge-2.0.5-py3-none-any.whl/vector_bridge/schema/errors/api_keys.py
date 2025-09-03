from enum import Enum
from typing import Type


class APIError(Exception):
    """Base class for API-related errors."""


class APIKeyNotFound(APIError):
    """Raised when the API key was not found."""


class APIKeyNotCreated(APIError):
    """Raised when the API key was not created."""


class APIGenericError(APIError):
    """Raised when an unspecified error occurs."""


class APIErrorDetail(str, Enum):
    KEY_NOT_FOUND = "API key was not found"
    KEY_NOT_CREATED = "API key was not created"
    GENERIC_ERROR = "Something went wrong. Try again later"

    def to_exception(self) -> Type[APIError]:
        """Return the exception class that corresponds to this error detail."""
        mapping = {
            APIErrorDetail.KEY_NOT_FOUND: APIKeyNotFound,
            APIErrorDetail.KEY_NOT_CREATED: APIKeyNotCreated,
            APIErrorDetail.GENERIC_ERROR: APIGenericError,
        }
        return mapping[self]


def raise_for_api_key_detail(detail: str) -> None:
    """
    Raises the corresponding APIError based on the given error detail string.
    """
    try:
        detail_enum = APIErrorDetail(detail)
    except ValueError:
        raise APIError(f"Unknown API error: {detail}")
    raise detail_enum.to_exception()(detail)
