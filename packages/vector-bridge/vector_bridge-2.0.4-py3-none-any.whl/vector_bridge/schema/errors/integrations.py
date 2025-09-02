from enum import Enum
from typing import Type


class IntegrationError(Exception):
    """Base class for Integration-related errors."""


class CrossOrgAccessNotAllowed(IntegrationError):
    """Raised when trying to access users from another organization."""


class DuplicateWeaviateInstanceNotAllowed(IntegrationError):
    """Raised when trying to use the same Weaviate instance for multiple integrations."""


class InvalidMaxSimilarityDistance(IntegrationError):
    """Raised when MAX_SIMILARITY_DISTANCE is not between 0 and 1."""


class IntegrationAlreadyExistsForOrganization(IntegrationError):
    """Raised when integration already exists for the organization."""


class IntegrationNotCreated(IntegrationError):
    """Raised when an integration was not created."""


class IntegrationGenericError(IntegrationError):
    """Raised for unspecified integration-related errors."""


class IntegrationNotFound(IntegrationError):
    """Raised when integration was not found."""


class IntegrationDeleteFailed(IntegrationError):
    """Raised when deletion of integrations failed."""


class IntegrationBulkUpdateFailed(IntegrationError):
    """Raised when bulk update of integrations failed."""


class OwnerRemovalNotAllowed(IntegrationError):
    """Raised when trying to remove the owner from an integration."""


class LastUserRemovalNotAllowed(IntegrationError):
    """Raised when trying to remove the last user from an integration."""


class UserIntegrationAlreadyExists(IntegrationError):
    """Raised when a user integration already exists."""


class UserIntegrationNotCreated(IntegrationError):
    """Raised when a user integration was not created."""


class UserIntegrationNotFound(IntegrationError):
    """Raised when a user integration was not found."""


class IntegrationErrorDetail(str, Enum):
    CROSS_ORG_ACCESS = "You can not access users from other organizations"
    DUPLICATE_WEAVIATE_INSTANCE = "You can not use the same weaviate instance for multiple integrations"
    INVALID_MAX_SIMILARITY_DISTANCE = "MAX_SIMILARITY_DISTANCE must be a float between 0 and 1"
    ALREADY_EXISTS_FOR_ORG = "Integration with this ID already exists for this organization"
    NOT_CREATED = "Integration was not created"
    GENERIC_ERROR = "Something went wrong. Try again later"
    NOT_FOUND = "Integration not found"
    DELETE_FAILED = "Failed to delete integrations"
    BULK_UPDATE_FAILED = "Failed to bulk update integrations"
    OWNER_REMOVAL_NOT_ALLOWED = "Owner can not be removed from integration."
    LAST_USER_REMOVAL_NOT_ALLOWED = "The last user can not be removed from integration."
    USER_INTEGRATION_ALREADY_EXISTS = "User integration with this ID already exists"
    USER_INTEGRATION_NOT_CREATED = "User integration was not created"
    USER_INTEGRATION_NOT_FOUND = "User integration not found"

    def to_exception(self) -> Type[IntegrationError]:
        """Return the exception class that corresponds to this integration error detail."""
        mapping = {
            IntegrationErrorDetail.CROSS_ORG_ACCESS: CrossOrgAccessNotAllowed,
            IntegrationErrorDetail.DUPLICATE_WEAVIATE_INSTANCE: DuplicateWeaviateInstanceNotAllowed,
            IntegrationErrorDetail.INVALID_MAX_SIMILARITY_DISTANCE: InvalidMaxSimilarityDistance,
            IntegrationErrorDetail.ALREADY_EXISTS_FOR_ORG: IntegrationAlreadyExistsForOrganization,
            IntegrationErrorDetail.NOT_CREATED: IntegrationNotCreated,
            IntegrationErrorDetail.GENERIC_ERROR: IntegrationGenericError,
            IntegrationErrorDetail.NOT_FOUND: IntegrationNotFound,
            IntegrationErrorDetail.DELETE_FAILED: IntegrationDeleteFailed,
            IntegrationErrorDetail.BULK_UPDATE_FAILED: IntegrationBulkUpdateFailed,
            IntegrationErrorDetail.OWNER_REMOVAL_NOT_ALLOWED: OwnerRemovalNotAllowed,
            IntegrationErrorDetail.LAST_USER_REMOVAL_NOT_ALLOWED: LastUserRemovalNotAllowed,
            IntegrationErrorDetail.USER_INTEGRATION_ALREADY_EXISTS: UserIntegrationAlreadyExists,
            IntegrationErrorDetail.USER_INTEGRATION_NOT_CREATED: UserIntegrationNotCreated,
            IntegrationErrorDetail.USER_INTEGRATION_NOT_FOUND: UserIntegrationNotFound,
        }
        return mapping[self]


def raise_for_integration_detail(detail: str) -> None:
    """
    Raises the corresponding IntegrationError based on the given integration error detail string.
    """
    try:
        detail_enum = IntegrationErrorDetail(detail)
    except ValueError:
        raise IntegrationError(f"Unknown Integration error: {detail}")
    raise detail_enum.to_exception()(detail)
