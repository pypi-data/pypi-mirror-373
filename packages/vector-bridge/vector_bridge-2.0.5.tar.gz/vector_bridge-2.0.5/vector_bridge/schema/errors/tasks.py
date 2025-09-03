from enum import Enum
from typing import Type


class TaskError(Exception):
    """Base class for Task-related errors."""


class SubtaskNotFound(TaskError):
    """Raised when the subtask was not found."""


class CommentNotFound(TaskError):
    """Raised when the comment was not found."""


class CommentDeleteNotAllowed(TaskError):
    """Raised when a user tries to delete a comment they do not own."""


class TaskAlreadyExistsForIntegration(TaskError):
    """Raised when a task with this ID already exists for the integration."""


class TaskNotCreated(TaskError):
    """Raised when a task was not created."""


class TaskNotFound(TaskError):
    """Raised when the task was not found."""


class TaskGenericError(TaskError):
    """Raised for unspecified task-related errors."""


class CommentAddFailed(TaskError):
    """Raised when adding a comment fails."""


class CommentRemoveFailed(TaskError):
    """Raised when removing a comment fails."""


class SubtaskAddFailed(TaskError):
    """Raised when adding a subtask fails."""


class SubtaskRemoveFailed(TaskError):
    """Raised when removing a subtask fails."""


class SubtaskCompletionUpdateFailed(TaskError):
    """Raised when updating subtask completion fails."""


class DictionaryItemDeleteFailed(TaskError):
    """Raised when deleting an item from the dictionary fails."""


class AllTasksDeleteFailed(TaskError):
    """Raised when deleting all tasks fails."""


class TaskErrorDetail(str, Enum):
    SUBTASK_NOT_FOUND = "Subtask not found"
    COMMENT_NOT_FOUND = "Comment not found"
    COMMENT_DELETE_NOT_ALLOWED = "You can only delete your own comments"
    ALREADY_EXISTS_FOR_INTEGRATION = "Task with this ID already exists for this integration"
    NOT_CREATED = "Task was not created"
    NOT_FOUND = "Task not found"
    GENERIC_ERROR = "Something went wrong. Try again later"
    COMMENT_ADD_FAILED = "Failed to add comment"
    COMMENT_REMOVE_FAILED = "Failed to remove comment"
    SUBTASK_ADD_FAILED = "Failed to add subtask"
    SUBTASK_REMOVE_FAILED = "Failed to remove subtask"
    SUBTASK_COMPLETION_UPDATE_FAILED = "Failed to update subtask completion"
    DICTIONARY_ITEM_DELETE_FAILED = "Failed to delete an item from the dictionary"
    ALL_TASKS_DELETE_FAILED = "Failed to delete all tasks"

    def to_exception(self) -> Type[TaskError]:
        """Return the exception class that corresponds to this task error detail."""
        mapping = {
            TaskErrorDetail.SUBTASK_NOT_FOUND: SubtaskNotFound,
            TaskErrorDetail.COMMENT_NOT_FOUND: CommentNotFound,
            TaskErrorDetail.COMMENT_DELETE_NOT_ALLOWED: CommentDeleteNotAllowed,
            TaskErrorDetail.ALREADY_EXISTS_FOR_INTEGRATION: TaskAlreadyExistsForIntegration,
            TaskErrorDetail.NOT_CREATED: TaskNotCreated,
            TaskErrorDetail.NOT_FOUND: TaskNotFound,
            TaskErrorDetail.GENERIC_ERROR: TaskGenericError,
            TaskErrorDetail.COMMENT_ADD_FAILED: CommentAddFailed,
            TaskErrorDetail.COMMENT_REMOVE_FAILED: CommentRemoveFailed,
            TaskErrorDetail.SUBTASK_ADD_FAILED: SubtaskAddFailed,
            TaskErrorDetail.SUBTASK_REMOVE_FAILED: SubtaskRemoveFailed,
            TaskErrorDetail.SUBTASK_COMPLETION_UPDATE_FAILED: SubtaskCompletionUpdateFailed,
            TaskErrorDetail.DICTIONARY_ITEM_DELETE_FAILED: DictionaryItemDeleteFailed,
            TaskErrorDetail.ALL_TASKS_DELETE_FAILED: AllTasksDeleteFailed,
        }
        return mapping[self]


def raise_for_task_detail(detail: str) -> None:
    """
    Raises the corresponding TaskError based on the given task error detail string.
    """
    try:
        detail_enum = TaskErrorDetail(detail)
    except ValueError:
        raise TaskError(f"Unknown Task error: {detail}")
    raise detail_enum.to_exception()(detail)
