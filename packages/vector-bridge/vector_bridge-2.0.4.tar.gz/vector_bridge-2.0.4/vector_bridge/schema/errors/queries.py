from enum import Enum
from typing import Type


class QueryError(Exception):
    """Base class for Query-related errors."""


class UUIDNotProvided(QueryError):
    """Raised when the UUID is not provided."""


class ContentHashAlreadyProcessed(QueryError):
    """Raised when content with the same hash is already processed."""


class VectorDBConnectionFailed(QueryError):
    """Raised when unable to connect to the Vector DB."""


class QueryErrorDetail(str, Enum):
    UUID_NOT_PROVIDED = "uuid is not provided"
    CONTENT_HASH_ALREADY_PROCESSED = "The content with the same hash is already processed"
    VECTOR_DB_CONNECTION_FAILED = "Unable to connect to the Vector DB"

    def to_exception(self) -> Type[QueryError]:
        """Return the exception class that corresponds to this query error detail."""
        mapping = {
            QueryErrorDetail.UUID_NOT_PROVIDED: UUIDNotProvided,
            QueryErrorDetail.CONTENT_HASH_ALREADY_PROCESSED: ContentHashAlreadyProcessed,
            QueryErrorDetail.VECTOR_DB_CONNECTION_FAILED: VectorDBConnectionFailed,
        }
        return mapping[self]


def raise_for_query_detail(detail: str) -> None:
    """
    Raises the corresponding QueryError based on the given query error detail string.
    """
    try:
        detail_enum = QueryErrorDetail(detail)
    except ValueError:
        raise QueryError(f"Unknown Query error: {detail}")
    raise detail_enum.to_exception()(detail)
