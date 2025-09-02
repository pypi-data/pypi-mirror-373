from enum import Enum
from typing import Type


class UserError(Exception):
    """Base class for User-related errors."""


class OrganizationIdAssignmentNotAllowed(UserError):
    """Raised when organization ID is assigned by unauthorized user."""


class UserNotFound(UserError):
    """Raised when the user is not found."""


class UserAccessDenied(UserError):
    """Raised when trying to access users from other organizations."""


class OwnerDeletionNotAllowed(UserError):
    """Raised when attempting to delete an owner user."""


class UserDisableNotAllowed(UserError):
    """Raised when trying to disable users outside your organization."""


class UserErrorDetail(str, Enum):
    ORG_ID_ASSIGNMENT_NOT_ALLOWED = (
        "Organization id can only be assigned by organization owner or when the organization was created"
    )
    NOT_FOUND = "User is not found"
    ACCESS_DENIED = "You can not access users from other organizations"
    OWNER_DELETION_NOT_ALLOWED = "Owner can not be deleted"
    DISABLE_NOT_ALLOWED = "You can only disable users within your own organization"

    def to_exception(self) -> Type[UserError]:
        """Return the exception class that corresponds to this user error detail."""
        mapping = {
            UserErrorDetail.ORG_ID_ASSIGNMENT_NOT_ALLOWED: OrganizationIdAssignmentNotAllowed,
            UserErrorDetail.NOT_FOUND: UserNotFound,
            UserErrorDetail.ACCESS_DENIED: UserAccessDenied,
            UserErrorDetail.OWNER_DELETION_NOT_ALLOWED: OwnerDeletionNotAllowed,
            UserErrorDetail.DISABLE_NOT_ALLOWED: UserDisableNotAllowed,
        }
        return mapping[self]


def raise_for_user_detail(detail: str) -> None:
    """
    Raises the corresponding UserError based on the given user error detail string.
    """
    try:
        detail_enum = UserErrorDetail(detail)
    except ValueError:
        raise UserError(f"Unknown User error: {detail}")
    raise detail_enum.to_exception()(detail)
