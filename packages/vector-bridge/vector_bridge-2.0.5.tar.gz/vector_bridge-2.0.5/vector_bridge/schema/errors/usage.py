from enum import Enum
from typing import Type


class UsageError(Exception):
    """Base class for Usage-related errors."""


class RequestUsageNotFound(UsageError):
    """Raised when a RequestUsage entry was not found."""


class RequestUsageAlreadyExists(UsageError):
    """Raised when a RequestUsage entry with the same primary key already exists."""


class RequestUsageNotCreated(UsageError):
    """Raised when a RequestUsage entry was not created."""


class UsageGenericError(UsageError):
    """Raised for unspecified usage-related errors."""


class UsageStatisticsFetchFailed(UsageError):
    """Raised when getting usage statistics fails."""


class DailyUsageStatisticsFetchFailed(UsageError):
    """Raised when getting daily usage statistics fails."""


class UsageErrorDetail(str, Enum):
    NOT_FOUND = "RequestUsage not found"
    ALREADY_EXISTS = "RequestUsage with this primary key already exists"
    NOT_CREATED = "RequestUsage was not created"
    GENERIC_ERROR = "Something went wrong. Try again later"
    STATS_FETCH_FAILED = "Something went wrong while getting usage statistics"
    DAILY_STATS_FETCH_FAILED = "Something went wrong while getting daily usage statistics"

    def to_exception(self) -> Type[UsageError]:
        """Return the exception class that corresponds to this usage error detail."""
        mapping = {
            UsageErrorDetail.NOT_FOUND: RequestUsageNotFound,
            UsageErrorDetail.ALREADY_EXISTS: RequestUsageAlreadyExists,
            UsageErrorDetail.NOT_CREATED: RequestUsageNotCreated,
            UsageErrorDetail.GENERIC_ERROR: UsageGenericError,
            UsageErrorDetail.STATS_FETCH_FAILED: UsageStatisticsFetchFailed,
            UsageErrorDetail.DAILY_STATS_FETCH_FAILED: DailyUsageStatisticsFetchFailed,
        }
        return mapping[self]


def raise_for_usage_detail(detail: str) -> None:
    """
    Raises the corresponding UsageError based on the given usage error detail string.
    """
    try:
        detail_enum = UsageErrorDetail(detail)
    except ValueError:
        raise UsageError(f"Unknown Usage error: {detail}")
    raise detail_enum.to_exception()(detail)
