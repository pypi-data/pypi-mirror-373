from enum import Enum
from typing import Type


class VectorDBStateChangesetError(Exception):
    """Base class for VectorDB State Changeset-related errors."""


class FilterAlreadyExists(VectorDBStateChangesetError):
    """Raised when a filter with the same name already exists."""


class FilterLikeOnlyForText(VectorDBStateChangesetError):
    """Raised when LIKE filter is applied to a non-TEXT type."""


class FilterContainsOnlyForTextArray(VectorDBStateChangesetError):
    """Raised when CONTAINS_ALL or CONTAINS_ANY is applied to non-text[] type."""


class PropertyAlreadyExists(VectorDBStateChangesetError):
    """Raised when a property with the same name already exists."""


class PropertyAlreadyDeleted(VectorDBStateChangesetError):
    """Raised when a property was already deleted."""


class PropertyAboutToBeDeleted(VectorDBStateChangesetError):
    """Raised when a property with the same name is already about to be deleted."""


class PropertyAboutToBeCreated(VectorDBStateChangesetError):
    """Raised when a property with the same name is already about to be created."""


class ProtectedPropertiesChangeNotAllowed(VectorDBStateChangesetError):
    """Raised when trying to change protected properties."""


class PropertyDoesNotExist(VectorDBStateChangesetError):
    """Raised when a property does not exist."""


class SchemaAlreadyExists(VectorDBStateChangesetError):
    """Raised when a schema with the same name already exists."""


class SchemaAboutToBeDeleted(VectorDBStateChangesetError):
    """Raised when a schema with the same name is already about to be deleted."""


class SchemaAboutToBeCreated(VectorDBStateChangesetError):
    """Raised when a schema with the same name is already about to be created."""


class SchemaDoesNotExist(VectorDBStateChangesetError):
    """Raised when a schema does not exist."""


class ChunksSchemaDeletionNotAllowed(VectorDBStateChangesetError):
    """Raised when deleting the Chunks schema is not allowed."""


class ProtectedSchemaDeletionNotAllowed(VectorDBStateChangesetError):
    """Raised when deleting a protected schema is not allowed."""


class ProtectedSchemaChangeNotAllowed(VectorDBStateChangesetError):
    """Raised when changing a protected schema is not allowed."""


class SchemaWithSpecifiedNameDoesNotExist(VectorDBStateChangesetError):
    """Raised when schema with specified name does not exist."""


class ChunksSchemaDiscardNotAllowed(VectorDBStateChangesetError):
    """Raised when discarding the Chunks schema is not allowed."""


class SchemaChangesetDoesNotExist(VectorDBStateChangesetError):
    """Raised when schema changeset with specified name does not exist."""


class ChunksSchemaModificationNotAllowed(VectorDBStateChangesetError):
    """Raised when modifying the Chunks schema is not allowed."""


class RequiredPropertyChangeNotAllowed(VectorDBStateChangesetError):
    """Raised when changing a required property is not allowed."""


class PropertyChangesetDoesNotExist(VectorDBStateChangesetError):
    """Raised when property changeset with specified name does not exist."""


class FilterAboutToBeDeleted(VectorDBStateChangesetError):
    """Raised when filter with the same name is already about to be deleted."""


class FilterAboutToBeCreated(VectorDBStateChangesetError):
    """Raised when filter with the same name is already about to be created."""


class FilterDoesNotExist(VectorDBStateChangesetError):
    """Raised when a filter does not exist."""


class RequiredPropertyFilterDeletionNotAllowed(VectorDBStateChangesetError):
    """Raised when deleting a filter of a required property is not allowed."""


class FilterChangesetDoesNotExist(VectorDBStateChangesetError):
    """Raised when filter changeset with specified name does not exist."""


class RequiredPropertyFilterDiscardNotAllowed(VectorDBStateChangesetError):
    """Raised when discarding a filter of a required property is not allowed."""


class VectorDBStateChangesetErrorDetail(str, Enum):
    FILTER_ALREADY_EXISTS = "Filter with the same name already exists"
    FILTER_LIKE_ONLY_FOR_TEXT = "Filter LIKE can only be applied to a TEXT data type"
    FILTER_CONTAINS_ONLY_FOR_TEXT_ARRAY = (
        "Filter CONTAINS_ALL and CONTAINS_ANY can only be applied to a text[] data type"
    )
    PROPERTY_ALREADY_EXISTS = "Property with the same name already exists"
    PROPERTY_ALREADY_DELETED = "Property was already deleted. Consider restoring it instead"
    PROPERTY_ABOUT_TO_BE_DELETED = "Property with the same name already about to be deleted"
    PROPERTY_ABOUT_TO_BE_CREATED = "Property with the same name already about to be created"
    PROTECTED_PROPERTIES_CHANGE_NOT_ALLOWED = "You can not change the protected properties"
    PROPERTY_DOES_NOT_EXIST = "Property does not exists"
    SCHEMA_ALREADY_EXISTS = "Schema with the same name already exists"
    SCHEMA_ABOUT_TO_BE_DELETED = "Schema with the same name already about to be deleted"
    SCHEMA_ABOUT_TO_BE_CREATED = "Schema with the same name already about to be created"
    SCHEMA_DOES_NOT_EXIST = "Schema does not exist"
    CHUNKS_SCHEMA_DELETION_NOT_ALLOWED = "Deleting the Chunks schema is not allowed"
    PROTECTED_SCHEMA_DELETION_NOT_ALLOWED = "You can not delete the protected schema"
    PROTECTED_SCHEMA_CHANGE_NOT_ALLOWED = "You can not change the protected schema"
    SCHEMA_WITH_SPECIFIED_NAME_DOES_NOT_EXIST = "Schema with the specified name does not exist"
    CHUNKS_SCHEMA_DISCARD_NOT_ALLOWED = "Discarding the Chunks schema is not allowed"
    SCHEMA_CHANGESET_DOES_NOT_EXIST = "Schema changeset with the specified name does not exist"
    CHUNKS_SCHEMA_MODIFICATION_NOT_ALLOWED = "Modifying the Chunks schema is not allowed"
    REQUIRED_PROPERTY_CHANGE_NOT_ALLOWED = "You can not change the required property"
    PROPERTY_CHANGESET_DOES_NOT_EXIST = "Property changeset with the specified name does not exist"
    FILTER_ABOUT_TO_BE_DELETED = "Filter with the same name already about to be deleted"
    FILTER_ABOUT_TO_BE_CREATED = "Filter with the same name already about to be created"
    FILTER_DOES_NOT_EXIST = "Filter does not exist"
    REQUIRED_PROPERTY_FILTER_DELETION_NOT_ALLOWED = "You can not delete a filter of the required property"
    FILTER_CHANGESET_DOES_NOT_EXIST = "Filter changeset with the specified name does not exist"
    REQUIRED_PROPERTY_FILTER_DISCARD_NOT_ALLOWED = "You can not discard a filter of the required property"

    def to_exception(self) -> Type[VectorDBStateChangesetError]:
        """Return the exception class that corresponds to this VectorDB State Changeset error detail."""
        mapping = {
            VectorDBStateChangesetErrorDetail.FILTER_ALREADY_EXISTS: FilterAlreadyExists,
            VectorDBStateChangesetErrorDetail.FILTER_LIKE_ONLY_FOR_TEXT: FilterLikeOnlyForText,
            VectorDBStateChangesetErrorDetail.FILTER_CONTAINS_ONLY_FOR_TEXT_ARRAY: FilterContainsOnlyForTextArray,
            VectorDBStateChangesetErrorDetail.PROPERTY_ALREADY_EXISTS: PropertyAlreadyExists,
            VectorDBStateChangesetErrorDetail.PROPERTY_ALREADY_DELETED: PropertyAlreadyDeleted,
            VectorDBStateChangesetErrorDetail.PROPERTY_ABOUT_TO_BE_DELETED: PropertyAboutToBeDeleted,
            VectorDBStateChangesetErrorDetail.PROPERTY_ABOUT_TO_BE_CREATED: PropertyAboutToBeCreated,
            VectorDBStateChangesetErrorDetail.PROTECTED_PROPERTIES_CHANGE_NOT_ALLOWED: ProtectedPropertiesChangeNotAllowed,
            VectorDBStateChangesetErrorDetail.PROPERTY_DOES_NOT_EXIST: PropertyDoesNotExist,
            VectorDBStateChangesetErrorDetail.SCHEMA_ALREADY_EXISTS: SchemaAlreadyExists,
            VectorDBStateChangesetErrorDetail.SCHEMA_ABOUT_TO_BE_DELETED: SchemaAboutToBeDeleted,
            VectorDBStateChangesetErrorDetail.SCHEMA_ABOUT_TO_BE_CREATED: SchemaAboutToBeCreated,
            VectorDBStateChangesetErrorDetail.SCHEMA_DOES_NOT_EXIST: SchemaDoesNotExist,
            VectorDBStateChangesetErrorDetail.CHUNKS_SCHEMA_DELETION_NOT_ALLOWED: ChunksSchemaDeletionNotAllowed,
            VectorDBStateChangesetErrorDetail.PROTECTED_SCHEMA_DELETION_NOT_ALLOWED: ProtectedSchemaDeletionNotAllowed,
            VectorDBStateChangesetErrorDetail.PROTECTED_SCHEMA_CHANGE_NOT_ALLOWED: ProtectedSchemaChangeNotAllowed,
            VectorDBStateChangesetErrorDetail.SCHEMA_WITH_SPECIFIED_NAME_DOES_NOT_EXIST: SchemaWithSpecifiedNameDoesNotExist,
            VectorDBStateChangesetErrorDetail.CHUNKS_SCHEMA_DISCARD_NOT_ALLOWED: ChunksSchemaDiscardNotAllowed,
            VectorDBStateChangesetErrorDetail.SCHEMA_CHANGESET_DOES_NOT_EXIST: SchemaChangesetDoesNotExist,
            VectorDBStateChangesetErrorDetail.CHUNKS_SCHEMA_MODIFICATION_NOT_ALLOWED: ChunksSchemaModificationNotAllowed,
            VectorDBStateChangesetErrorDetail.REQUIRED_PROPERTY_CHANGE_NOT_ALLOWED: RequiredPropertyChangeNotAllowed,
            VectorDBStateChangesetErrorDetail.PROPERTY_CHANGESET_DOES_NOT_EXIST: PropertyChangesetDoesNotExist,
            VectorDBStateChangesetErrorDetail.FILTER_ABOUT_TO_BE_DELETED: FilterAboutToBeDeleted,
            VectorDBStateChangesetErrorDetail.FILTER_ABOUT_TO_BE_CREATED: FilterAboutToBeCreated,
            VectorDBStateChangesetErrorDetail.FILTER_DOES_NOT_EXIST: FilterDoesNotExist,
            VectorDBStateChangesetErrorDetail.REQUIRED_PROPERTY_FILTER_DELETION_NOT_ALLOWED: RequiredPropertyFilterDeletionNotAllowed,
            VectorDBStateChangesetErrorDetail.FILTER_CHANGESET_DOES_NOT_EXIST: FilterChangesetDoesNotExist,
            VectorDBStateChangesetErrorDetail.REQUIRED_PROPERTY_FILTER_DISCARD_NOT_ALLOWED: RequiredPropertyFilterDiscardNotAllowed,
        }
        return mapping[self]


def raise_for_vectordb_state_changeset_detail(detail: str) -> None:
    """
    Raises the corresponding VectorDBStateChangesetError based on the given error detail string.
    """
    try:
        detail_enum = VectorDBStateChangesetErrorDetail(detail)
    except ValueError:
        raise VectorDBStateChangesetError(f"Unknown VectorDB State Changeset error: {detail}")
    raise detail_enum.to_exception()(detail)
