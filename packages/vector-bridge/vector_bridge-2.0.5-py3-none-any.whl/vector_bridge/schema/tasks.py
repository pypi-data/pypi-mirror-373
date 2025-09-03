import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from vector_bridge import AsyncVectorBridgeClient, VectorBridgeClient


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    READY_FOR_REVIEW = "ready_for_review"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TasksSorting(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    priority = "priority"
    due_date = "due_date"
    position = "position"


class TaskMoveRequest(BaseModel):
    status: TaskStatus
    destination_index: int


class HistoryChangeType(str, Enum):
    TASK_CREATED = "task_created"
    FIELD_CHANGED = "field_changed"
    COMMENT_ADDED = "comment_added"
    COMMENT_DELETED = "comment_deleted"
    SUBTASK_ADDED = "subtask_added"
    SUBTASK_DELETED = "subtask_deleted"
    SUBTASK_COMPLETED = "subtask_completed"
    SUBTASK_REOPENED = "subtask_reopened"
    LABELS_ADDED = "labels_added"
    LABELS_REMOVED = "labels_removed"


class SubtaskCreate(BaseModel):
    title: str = Field(..., description="The title of the subtask")
    description: Optional[str] = Field(None, description="The description of the subtask")


class Subtask(BaseModel):
    subtask_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="The title of the subtask")
    description: Optional[str] = Field(None, description="The description of the subtask")
    completed: bool = Field(default=False, description="Whether the subtask is completed")
    created_at: datetime = Field(..., description="When the subtask was created")
    updated_at: datetime = Field(..., description="When the subtask was last updated")

    def delete(self, client: VectorBridgeClient, task_id: str) -> "Task":
        """Delete this subtask from its parent task."""
        return client.admin.tasks.delete_subtask(task_id=task_id, subtask_id=self.subtask_id)

    async def a_delete(self, client: AsyncVectorBridgeClient, task_id: str) -> "Task":
        """Asynchronously delete this subtask from its parent task."""
        return await client.admin.tasks.delete_subtask(task_id=task_id, subtask_id=self.subtask_id)

    def toggle_completion(self, client: VectorBridgeClient, task_id: str) -> "Task":
        """Toggle this subtask's completion status."""
        return client.admin.tasks.toggle_subtask_completion(
            task_id=task_id, subtask_id=self.subtask_id, completed=not self.completed
        )

    async def a_toggle_completion(self, client: AsyncVectorBridgeClient, task_id: str) -> "Task":
        """Asynchronously toggle this subtask's completion status."""
        return await client.admin.tasks.toggle_subtask_completion(
            task_id=task_id, subtask_id=self.subtask_id, completed=not self.completed
        )

    def mark_completed(self, client: VectorBridgeClient, task_id: str) -> "Task":
        """Mark this subtask as completed."""
        return client.admin.tasks.toggle_subtask_completion(task_id=task_id, subtask_id=self.subtask_id, completed=True)

    async def a_mark_completed(self, client: AsyncVectorBridgeClient, task_id: str) -> "Task":
        """Asynchronously mark this subtask as completed."""
        return await client.admin.tasks.toggle_subtask_completion(
            task_id=task_id, subtask_id=self.subtask_id, completed=True
        )

    def mark_incomplete(self, client: VectorBridgeClient, task_id: str) -> "Task":
        """Mark this subtask as incomplete."""
        return client.admin.tasks.toggle_subtask_completion(
            task_id=task_id, subtask_id=self.subtask_id, completed=False
        )

    async def a_mark_incomplete(self, client: AsyncVectorBridgeClient, task_id: str) -> "Task":
        """Asynchronously mark this subtask as incomplete."""
        return await client.admin.tasks.toggle_subtask_completion(
            task_id=task_id, subtask_id=self.subtask_id, completed=False
        )


class CommentCreate(BaseModel):
    text: str = Field(..., description="The comment text")


class Comment(BaseModel):
    comment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(..., description="The comment text")
    author_id: str = Field(..., description="The ID of the comment author")
    created_at: datetime = Field(..., description="When the comment was created")


class TaskHistoryEntry(BaseModel):
    history_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    change_type: HistoryChangeType = Field(..., description="The type of change")
    field_name: Optional[str] = Field(None, description="The name of the field that changed")
    old_value: Optional[Union[str, int, float, bool, List[str]]] = Field(None, description="The old value")
    new_value: Optional[Union[str, int, float, bool, List[str]]] = Field(None, description="The new value")
    changed_by: str = Field(..., description="The ID of the user who made the change")
    changed_at: datetime = Field(..., description="When the change was made")
    additional_data: Optional[dict] = Field(None, description="Additional data related to the change")


class TaskCreate(BaseModel):
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="The status of the task")
    assignee: Optional[str] = Field(None, description="The assignee of the task")
    reporter: Optional[str] = Field(None, description="The reporter of the task")
    labels: List[str] = Field(default_factory=list, description="The labels of the task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="The priority of the task")
    start_date: Optional[datetime] = Field(None, description="The start date of the task")
    end_date: Optional[datetime] = Field(None, description="The end date of the task")

    def to_task(
        self,
        *,
        integration_id: str,
        created_by: str,
        updated_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        subtasks: Optional[List[Subtask]] = None,
        comments: Optional[List[Comment]] = None,
    ) -> "Task":
        now = datetime.now(timezone.utc)
        created_at = created_at or now
        updated_at = updated_at or now
        updated_by = updated_by or created_by

        return Task(
            integration_id=integration_id,
            title=self.title,
            description=self.description,
            status=self.status,
            assignee=self.assignee,
            reporter=self.reporter,
            labels=list(self.labels),
            priority=self.priority,
            start_date=self.start_date,
            end_date=self.end_date,
            subtasks=subtasks or [],
            comments=comments or [],
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
        )


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    assignee: Optional[str] = Field(None, description="The assignee of the task")
    reporter: Optional[str] = Field(None, description="The reporter of the task")
    labels: Optional[List[str]] = Field(None, description="The labels of the task")
    priority: Optional[TaskPriority] = Field(None, description="The priority of the task")
    start_date: Optional[datetime] = Field(None, description="The start date of the task")
    end_date: Optional[datetime] = Field(None, description="The end date of the task")


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str = Field(..., description="The ID of the integration")
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    status: TaskStatus = Field(..., description="The status of the task")
    assignee: Optional[str] = Field(None, description="The assignee of the task")
    reporter: Optional[str] = Field(None, description="The reporter of the task")
    labels: List[str] = Field(default_factory=list, description="The labels of the task")
    priority: TaskPriority = Field(..., description="The priority of the task")
    start_date: Optional[datetime] = Field(None, description="The start date of the task")
    end_date: Optional[datetime] = Field(None, description="The end date of the task")
    subtasks: List[Subtask] = Field(default_factory=list, description="The subtasks of the task")
    comments: List[Comment] = Field(default_factory=list, description="The comments on the task")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: datetime = Field(..., description="When the task was last updated")
    created_by: str = Field(..., description="Who created the task")
    updated_by: str = Field(..., description="Who last updated the task")

    def delete(self, client: VectorBridgeClient) -> None:
        """Delete this task."""
        client.admin.tasks.delete_task(task_id=self.task_id)

    async def a_delete(self, client: AsyncVectorBridgeClient) -> None:
        """Asynchronously delete this task."""
        await client.admin.tasks.delete_task(task_id=self.task_id)

    def update_status(self, client: VectorBridgeClient, status: TaskStatus) -> "Task":
        """Update this task's status."""
        return client.admin.tasks.update_task_status(task_id=self.task_id, status=status)

    async def a_update_status(self, client: AsyncVectorBridgeClient, status: TaskStatus) -> "Task":
        """Asynchronously update this task's status."""
        return await client.admin.tasks.update_task_status(task_id=self.task_id, status=status)

    def update_details(self, client: VectorBridgeClient, task_update: "TaskUpdate") -> "Task":
        """Update this task's details."""
        return client.admin.tasks.update_task_details(task_id=self.task_id, task_update=task_update)

    async def a_update_details(self, client: AsyncVectorBridgeClient, task_update: "TaskUpdate") -> "Task":
        """Asynchronously update this task's details."""
        return await client.admin.tasks.update_task_details(task_id=self.task_id, task_update=task_update)

    def add_subtask(self, client: VectorBridgeClient, subtask_create: "SubtaskCreate") -> "Task":
        """Add a subtask to this task."""
        return client.admin.tasks.add_subtask(task_id=self.task_id, subtask_create=subtask_create)

    async def a_add_subtask(self, client: AsyncVectorBridgeClient, subtask_create: "SubtaskCreate") -> "Task":
        """Asynchronously add a subtask to this task."""
        return await client.admin.tasks.add_subtask(task_id=self.task_id, subtask_create=subtask_create)

    def add_comment(self, client: VectorBridgeClient, comment_create: "CommentCreate") -> "Task":
        """Add a comment to this task."""
        return client.admin.tasks.add_comment(task_id=self.task_id, comment_create=comment_create)

    async def a_add_comment(self, client: AsyncVectorBridgeClient, comment_create: "CommentCreate") -> "Task":
        """Asynchronously add a comment to this task."""
        return await client.admin.tasks.add_comment(task_id=self.task_id, comment_create=comment_create)

    def refresh(self, client: VectorBridgeClient) -> Optional["Task"]:
        """Refresh this task's data from the server."""
        return client.admin.tasks.get_task_by_id(task_id=self.task_id)

    async def a_refresh(self, client: AsyncVectorBridgeClient) -> Optional["Task"]:
        """Asynchronously refresh this task's data from the server."""
        return await client.admin.tasks.get_task_by_id(task_id=self.task_id)

    def delete_comment_by_id(self, client: "VectorBridgeClient", comment_id: str) -> "Task":
        """Delete a specific comment from this task by comment ID."""
        return client.admin.tasks.delete_comment(task_id=self.task_id, comment_id=comment_id)

    async def a_delete_comment_by_id(self, client: "AsyncVectorBridgeClient", comment_id: str) -> "Task":
        """Asynchronously delete a specific comment from this task by comment ID."""
        return await client.admin.tasks.delete_comment(task_id=self.task_id, comment_id=comment_id)

    # Convenience properties
    @property
    def is_todo(self) -> bool:
        """Check if the task is in TODO status."""
        return self.status == TaskStatus.TODO

    @property
    def is_in_progress(self) -> bool:
        """Check if the task is in progress."""
        return self.status == TaskStatus.IN_PROGRESS

    @property
    def is_done(self) -> bool:
        """Check if the task is done."""
        return self.status == TaskStatus.DONE

    @property
    def is_cancelled(self) -> bool:
        """Check if the task is cancelled."""
        return self.status == TaskStatus.CANCELLED

    @property
    def is_overdue(self) -> bool:
        """Check if the task is overdue based on end_date."""
        if not self.end_date:
            return False
        return datetime.now(timezone.utc) > self.end_date

    @property
    def completed_subtasks_count(self) -> int:
        """Get the number of completed subtasks."""
        return sum(1 for subtask in self.subtasks if subtask.completed)

    @property
    def total_subtasks_count(self) -> int:
        """Get the total number of subtasks."""
        return len(self.subtasks)

    @property
    def comments_count(self) -> int:
        """Get the number of comments."""
        return len(self.comments)


class PaginatedTasks(BaseModel):
    tasks: List[Task] = Field(..., description="The list of tasks")
    last_evaluated_key: Optional[str] = Field(None, description="The key for pagination")
    has_more: bool = Field(..., description="Whether there are more tasks")
