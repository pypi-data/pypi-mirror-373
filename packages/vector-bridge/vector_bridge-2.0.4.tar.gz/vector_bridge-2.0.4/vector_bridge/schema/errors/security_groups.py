from enum import Enum
from typing import Type


class SecurityGroupError(Exception):
    """Base class for Security Group-related errors."""


class SecurityGroupNotFound(SecurityGroupError):
    """Raised when the security group was not found."""


class SecurityGroupNameAlreadyExists(SecurityGroupError):
    """Raised when a security group with this name already exists in the organization."""


class UserNotAddedToIntegration(SecurityGroupError):
    """Raised when the user was not added to the integration."""


class SecurityGroupAlreadyExists(SecurityGroupError):
    """Raised when a security group with this ID already exists."""


class SecurityGroupCreationFailed(SecurityGroupError):
    """Raised when creating a security group fails."""


class SecurityGroupFetchFailed(SecurityGroupError):
    """Raised when fetching a security group fails."""


class SecurityGroupBatchFetchFailed(SecurityGroupError):
    """Raised when fetching a batch of security groups fails."""


class SecurityGroupPermissionsUpdateFailed(SecurityGroupError):
    """Raised when updating security group permissions fails."""


class SecurityGroupDeleteFailed(SecurityGroupError):
    """Raised when deleting a security group fails."""


class SecurityGroupGenericError(SecurityGroupError):
    """Raised for unspecified security group-related errors."""


class SecurityGroupErrorDetail(str, Enum):
    NOT_FOUND = "Security group not found"
    NAME_ALREADY_EXISTS = "A security group with this name already exists in the organization"
    USER_NOT_ADDED_TO_INTEGRATION = "The user was not added to the integration"
    ALREADY_EXISTS = "Security Group with this ID already exists"
    CREATION_FAILED = "Failed to create Security Group"
    FETCH_FAILED = "Failed to fetch Security Group"
    BATCH_FETCH_FAILED = "Failed to fetch batch of Security Groups"
    PERMISSIONS_UPDATE_FAILED = "Failed to update Security Group permissions"
    DELETE_FAILED = "Failed to delete Security Group"
    GENERIC_ERROR = "Something went wrong. Try again later"

    def to_exception(self) -> Type[SecurityGroupError]:
        """Return the exception class that corresponds to this security group error detail."""
        mapping = {
            SecurityGroupErrorDetail.NOT_FOUND: SecurityGroupNotFound,
            SecurityGroupErrorDetail.NAME_ALREADY_EXISTS: SecurityGroupNameAlreadyExists,
            SecurityGroupErrorDetail.USER_NOT_ADDED_TO_INTEGRATION: UserNotAddedToIntegration,
            SecurityGroupErrorDetail.ALREADY_EXISTS: SecurityGroupAlreadyExists,
            SecurityGroupErrorDetail.CREATION_FAILED: SecurityGroupCreationFailed,
            SecurityGroupErrorDetail.FETCH_FAILED: SecurityGroupFetchFailed,
            SecurityGroupErrorDetail.BATCH_FETCH_FAILED: SecurityGroupBatchFetchFailed,
            SecurityGroupErrorDetail.PERMISSIONS_UPDATE_FAILED: SecurityGroupPermissionsUpdateFailed,
            SecurityGroupErrorDetail.DELETE_FAILED: SecurityGroupDeleteFailed,
            SecurityGroupErrorDetail.GENERIC_ERROR: SecurityGroupGenericError,
        }
        return mapping[self]


def raise_for_security_group_detail(detail: str) -> None:
    """
    Raises the corresponding SecurityGroupError based on the given security group error detail string.
    """
    try:
        detail_enum = SecurityGroupErrorDetail(detail)
    except ValueError:
        raise SecurityGroupError(f"Unknown Security Group error: {detail}")
    raise detail_enum.to_exception()(detail)
