from enum import Enum
from typing import Type


class FunctionError(Exception):
    """Base class for Function-related errors."""


class FunctionAlreadyExists(FunctionError):
    """Raised when a function with the same name already exists."""


class FunctionDeletionNotAllowed(FunctionError):
    """Raised when a specified function cannot be deleted."""


class FunctionAlreadyExistsForIntegration(FunctionError):
    """Raised when a function with this name already exists for this integration."""


class FunctionNotCreated(FunctionError):
    """Raised when a function was not created."""


class FunctionNotFound(FunctionError):
    """Raised when a function could not be found."""


class FunctionGenericError(FunctionError):
    """Raised for unspecified function-related errors."""


class FunctionBulkOperationFailed(FunctionError):
    """Raised when a bulk operation failed."""


class FunctionBulkDeleteFailed(FunctionError):
    """Raised when a bulk delete operation failed."""


class FunctionErrorDetail(str, Enum):
    ALREADY_EXISTS = "Function with the same name already exists"
    DELETION_NOT_ALLOWED = "Specified Function can not be deleted"
    ALREADY_EXISTS_FOR_INTEGRATION = "Function with this name already exists for this integration"
    NOT_CREATED = "Function was not created"
    NOT_FOUND = "Function not found"
    GENERIC_ERROR = "Something went wrong. Try again later"
    BULK_OPERATION_FAILED = "Bulk operation failed"
    BULK_DELETE_FAILED = "Bulk delete operation failed"

    def to_exception(self) -> Type[FunctionError]:
        """Return the exception class that corresponds to this function error detail."""
        mapping = {
            FunctionErrorDetail.ALREADY_EXISTS: FunctionAlreadyExists,
            FunctionErrorDetail.DELETION_NOT_ALLOWED: FunctionDeletionNotAllowed,
            FunctionErrorDetail.ALREADY_EXISTS_FOR_INTEGRATION: FunctionAlreadyExistsForIntegration,
            FunctionErrorDetail.NOT_CREATED: FunctionNotCreated,
            FunctionErrorDetail.NOT_FOUND: FunctionNotFound,
            FunctionErrorDetail.GENERIC_ERROR: FunctionGenericError,
            FunctionErrorDetail.BULK_OPERATION_FAILED: FunctionBulkOperationFailed,
            FunctionErrorDetail.BULK_DELETE_FAILED: FunctionBulkDeleteFailed,
        }
        return mapping[self]


def raise_for_function_detail(detail: str) -> None:
    """
    Raises the corresponding FunctionError based on the given function error detail string.
    """
    try:
        detail_enum = FunctionErrorDetail(detail)
    except ValueError:
        raise FunctionError(f"Unknown Function error: {detail}")
    raise detail_enum.to_exception()(detail)
