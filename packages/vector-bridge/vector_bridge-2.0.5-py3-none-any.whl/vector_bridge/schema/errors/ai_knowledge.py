from enum import Enum
from typing import Type


class ContentError(Exception):
    """Base class for Content-related errors."""


class ContentHashAlreadyProcessed(ContentError):
    """Raised when content with the same hash is already processed."""


class InvalidSignature(ContentError):
    """Raised when signature is invalid."""


class FileServeFailed(ContentError):
    """Raised when failed to serve a file."""


class InvalidPolicyMissingExpiration(ContentError):
    """Raised when policy is invalid due to missing expiration."""


class KeyMismatchPolicy(ContentError):
    """Raised when key in request doesn't match policy."""


class InvalidKeyFormat(ContentError):
    """Raised when key format is invalid."""


class InvalidPolicyFormat(ContentError):
    """Raised when policy format is invalid."""


class FolderOrFileNotExist(ContentError):
    """Raised when folder or file does not exist."""


class FolderNameAlreadyExists(ContentError):
    """Raised when folder with the same name is already created."""


class FileNameAlreadyExists(ContentError):
    """Raised when file with the same name is already created."""


class FileOrFolderNameAlreadyExists(ContentError):
    """Raised when file or folder with the same name is already created."""


class FileContentAlreadyExists(ContentError):
    """Raised when file with the same content is already created."""


class ParentFolderNotExist(ContentError):
    """Raised when parent folder does not exist."""


class FolderOrFileIsPrivate(ContentError):
    """Raised when folder or file is private."""


class TargetFolderOrFileIsPrivate(ContentError):
    """Raised when target folder or file is private."""


class OnlyEmptyFolderCanBeDeleted(ContentError):
    """Raised when only an empty folder can be deleted."""


class FolderCannotBeMoved(ContentError):
    """Raised when folder cannot be moved."""


class TargetFolderNotExist(ContentError):
    """Raised when the target folder does not exist."""


class DeleteFileOrFolderFailed(ContentError):
    """Raised when failed to delete a file or a folder."""


class ContentErrorDetail(str, Enum):
    CONTENT_HASH_ALREADY_PROCESSED = "The content with the same hash is already processed"
    INVALID_SIGNATURE = "Invalid signature"
    FILE_SERVE_FAILED = "Failed to serve file"
    INVALID_POLICY_MISSING_EXPIRATION = "Invalid policy: missing expiration"
    KEY_MISMATCH_POLICY = "Key in request doesn't match policy"
    INVALID_KEY_FORMAT = "Invalid key format"
    INVALID_POLICY_FORMAT = "Invalid policy format"
    FOLDER_OR_FILE_NOT_EXIST = "Folder or file does not exist"
    FOLDER_NAME_ALREADY_EXISTS = "Folder with the same name is already created"
    FILE_NAME_ALREADY_EXISTS = "File with the same name is already created"
    FILE_OR_FOLDER_NAME_ALREADY_EXISTS = "File or Folder with the same name is already created"
    FILE_CONTENT_ALREADY_EXISTS = "File with the same content is already created"
    PARENT_FOLDER_NOT_EXIST = "Parent folder does not exist"
    FOLDER_OR_FILE_IS_PRIVATE = "Folder or file is private"
    TARGET_FOLDER_OR_FILE_IS_PRIVATE = "Target folder or file is private"
    ONLY_EMPTY_FOLDER_CAN_BE_DELETED = "Only an empty folder can be deleted"
    FOLDER_CANNOT_BE_MOVED = "Folder can not be moved"
    TARGET_FOLDER_NOT_EXIST = "The target folder does not exist"
    DELETE_FILE_OR_FOLDER_FAILED = "Failed to delete a file or a folder"

    def to_exception(self) -> Type[ContentError]:
        """Return the exception class that corresponds to this content error detail."""
        mapping = {
            ContentErrorDetail.CONTENT_HASH_ALREADY_PROCESSED: ContentHashAlreadyProcessed,
            ContentErrorDetail.INVALID_SIGNATURE: InvalidSignature,
            ContentErrorDetail.FILE_SERVE_FAILED: FileServeFailed,
            ContentErrorDetail.INVALID_POLICY_MISSING_EXPIRATION: InvalidPolicyMissingExpiration,
            ContentErrorDetail.KEY_MISMATCH_POLICY: KeyMismatchPolicy,
            ContentErrorDetail.INVALID_KEY_FORMAT: InvalidKeyFormat,
            ContentErrorDetail.INVALID_POLICY_FORMAT: InvalidPolicyFormat,
            ContentErrorDetail.FOLDER_OR_FILE_NOT_EXIST: FolderOrFileNotExist,
            ContentErrorDetail.FOLDER_NAME_ALREADY_EXISTS: FolderNameAlreadyExists,
            ContentErrorDetail.FILE_NAME_ALREADY_EXISTS: FileNameAlreadyExists,
            ContentErrorDetail.FILE_OR_FOLDER_NAME_ALREADY_EXISTS: FileOrFolderNameAlreadyExists,
            ContentErrorDetail.FILE_CONTENT_ALREADY_EXISTS: FileContentAlreadyExists,
            ContentErrorDetail.PARENT_FOLDER_NOT_EXIST: ParentFolderNotExist,
            ContentErrorDetail.FOLDER_OR_FILE_IS_PRIVATE: FolderOrFileIsPrivate,
            ContentErrorDetail.TARGET_FOLDER_OR_FILE_IS_PRIVATE: TargetFolderOrFileIsPrivate,
            ContentErrorDetail.ONLY_EMPTY_FOLDER_CAN_BE_DELETED: OnlyEmptyFolderCanBeDeleted,
            ContentErrorDetail.FOLDER_CANNOT_BE_MOVED: FolderCannotBeMoved,
            ContentErrorDetail.TARGET_FOLDER_NOT_EXIST: TargetFolderNotExist,
            ContentErrorDetail.DELETE_FILE_OR_FOLDER_FAILED: DeleteFileOrFolderFailed,
        }
        return mapping[self]


def raise_for_ai_knowledge_detail(detail: str) -> None:
    """
    Raises the corresponding ContentError based on the given content error detail string.
    """
    try:
        detail_enum = ContentErrorDetail(detail)
    except ValueError:
        raise ContentError(f"Unknown Content error: {detail}")
    raise detail_enum.to_exception()(detail)
