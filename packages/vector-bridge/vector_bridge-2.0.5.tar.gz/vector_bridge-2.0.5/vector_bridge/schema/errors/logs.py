from enum import Enum
from typing import Type


class LogError(Exception):
    """Base class for Log-related errors."""


class LogNotFound(LogError):
    """Raised when a log was not found."""


class LogAlreadyExistsForIntegration(LogError):
    """Raised when a log with this timestamp already exists for the integration."""


class LogNotCreated(LogError):
    """Raised when a log was not created."""


class LogGenericError(LogError):
    """Raised for unspecified log-related errors."""


class LogErrorDetail(str, Enum):
    NOT_FOUND = "Log not found"
    ALREADY_EXISTS_FOR_INTEGRATION = "Log with this timestamp already exists for this integration"
    NOT_CREATED = "Log was not created"
    GENERIC_ERROR = "Something went wrong. Try again later"

    def to_exception(self) -> Type[LogError]:
        """Return the exception class that corresponds to this log error detail."""
        mapping = {
            LogErrorDetail.NOT_FOUND: LogNotFound,
            LogErrorDetail.ALREADY_EXISTS_FOR_INTEGRATION: LogAlreadyExistsForIntegration,
            LogErrorDetail.NOT_CREATED: LogNotCreated,
            LogErrorDetail.GENERIC_ERROR: LogGenericError,
        }
        return mapping[self]


def raise_for_log_detail(detail: str) -> None:
    """
    Raises the corresponding LogError based on the given log error detail string.
    """
    try:
        detail_enum = LogErrorDetail(detail)
    except ValueError:
        raise LogError(f"Unknown Log error: {detail}")
    raise detail_enum.to_exception()(detail)
