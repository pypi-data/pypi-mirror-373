from enum import Enum
from typing import Type


class OrganizationError(Exception):
    """Base class for Organization-related errors."""


class OrganizationUpdateNotAllowed(OrganizationError):
    """Raised when the user does not have rights to update the organization."""


class UserAlreadyAssignedToOrganization(OrganizationError):
    """Raised when the user is already assigned to an organization."""


class OrganizationAlreadyExists(OrganizationError):
    """Raised when an organization with this ID already exists."""


class OrganizationNotCreated(OrganizationError):
    """Raised when an organization was not created."""


class OrganizationNotFound(OrganizationError):
    """Raised when an organization was not found."""


class OrganizationGenericError(OrganizationError):
    """Raised for unspecified organization-related errors."""


class StorageUsageUpdateFailed(OrganizationError):
    """Raised when updating storage usage fails."""


class StorageUsageFetchFailed(OrganizationError):
    """Raised when fetching storage usage fails."""


class OrganizationErrorDetail(str, Enum):
    UPDATE_NOT_ALLOWED = "You don't have rights to update this organization"
    USER_ALREADY_ASSIGNED = "The user is already assigned to an organization"
    ALREADY_EXISTS = "Organization with this ID already exists"
    NOT_CREATED = "Organization was not created"
    NOT_FOUND = "Organization not found"
    GENERIC_ERROR = "Something went wrong. Try again later"
    STORAGE_USAGE_UPDATE_FAILED = "Failed to update storage usage"
    STORAGE_USAGE_FETCH_FAILED = "Failed to fetch storage usage"

    def to_exception(self) -> Type[OrganizationError]:
        """Return the exception class that corresponds to this organization error detail."""
        mapping = {
            OrganizationErrorDetail.UPDATE_NOT_ALLOWED: OrganizationUpdateNotAllowed,
            OrganizationErrorDetail.USER_ALREADY_ASSIGNED: UserAlreadyAssignedToOrganization,
            OrganizationErrorDetail.ALREADY_EXISTS: OrganizationAlreadyExists,
            OrganizationErrorDetail.NOT_CREATED: OrganizationNotCreated,
            OrganizationErrorDetail.NOT_FOUND: OrganizationNotFound,
            OrganizationErrorDetail.GENERIC_ERROR: OrganizationGenericError,
            OrganizationErrorDetail.STORAGE_USAGE_UPDATE_FAILED: StorageUsageUpdateFailed,
            OrganizationErrorDetail.STORAGE_USAGE_FETCH_FAILED: StorageUsageFetchFailed,
        }
        return mapping[self]


def raise_for_organization_detail(detail: str) -> None:
    """
    Raises the corresponding OrganizationError based on the given organization error detail string.
    """
    try:
        detail_enum = OrganizationErrorDetail(detail)
    except ValueError:
        raise OrganizationError(f"Unknown Organization error: {detail}")
    raise detail_enum.to_exception()(detail)
