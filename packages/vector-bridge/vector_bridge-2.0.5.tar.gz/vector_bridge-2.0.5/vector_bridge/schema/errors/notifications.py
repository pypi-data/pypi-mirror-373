from enum import Enum
from typing import Type


class NotificationError(Exception):
    """Base class for Notification-related errors."""


class NotificationAlreadyExists(NotificationError):
    """Raised when a notification with this ID already exists."""


class NotificationNotCreated(NotificationError):
    """Raised when a notification was not created."""


class NotificationNotFound(NotificationError):
    """Raised when a notification was not found."""


class NotificationGenericError(NotificationError):
    """Raised for unspecified notification-related errors."""


class NotificationErrorDetail(str, Enum):
    ALREADY_EXISTS = "Notification with this ID already exists"
    NOT_CREATED = "Notification was not created"
    NOT_FOUND = "Notification not found"
    GENERIC_ERROR = "Something went wrong. Try again later"

    def to_exception(self) -> Type[NotificationError]:
        """Return the exception class that corresponds to this notification error detail."""
        mapping = {
            NotificationErrorDetail.ALREADY_EXISTS: NotificationAlreadyExists,
            NotificationErrorDetail.NOT_CREATED: NotificationNotCreated,
            NotificationErrorDetail.NOT_FOUND: NotificationNotFound,
            NotificationErrorDetail.GENERIC_ERROR: NotificationGenericError,
        }
        return mapping[self]


def raise_for_notification_detail(detail: str) -> None:
    """
    Raises the corresponding NotificationError based on the given notification error detail string.
    """
    try:
        detail_enum = NotificationErrorDetail(detail)
    except ValueError:
        raise NotificationError(f"Unknown Notification error: {detail}")
    raise detail_enum.to_exception()(detail)
