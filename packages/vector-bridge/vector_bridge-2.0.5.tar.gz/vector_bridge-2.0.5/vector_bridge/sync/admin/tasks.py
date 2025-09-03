import json
from typing import Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.tasks import raise_for_task_detail
from vector_bridge.schema.tasks import (CommentCreate, PaginatedTasks,
                                        SubtaskCreate, Task, TaskCreate,
                                        TaskMoveRequest, TasksSorting,
                                        TaskStatus, TaskUpdate)
from vector_bridge.utils import custom_json_serializer_datetime


class TasksAdmin:
    """Admin client for tasks management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def list_tasks(
        self,
        integration_name: str = None,
        limit: int = 1000,
        last_evaluated_key: Optional[str] = None,
        sort_by: TasksSorting = TasksSorting.created_at,
        status_filter: Optional[TaskStatus] = None,
        assignee_filter: Optional[str] = None,
        reporter_filter: Optional[str] = None,
    ) -> PaginatedTasks:
        """
        List all tasks for an Integration.

        Args:
            integration_name: The name of the Integration
            limit: The number of tasks to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: The sort field
            status_filter: Filter tasks by status
            assignee_filter: Filter tasks by assignee
            reporter_filter: Filter tasks by reporter

        Returns:
            PaginatedTasks with tasks and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/tasks/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "sort_by": sort_by,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key
        if status_filter:
            params["status_filter"] = status_filter
        if assignee_filter:
            params["assignee_filter"] = assignee_filter
        if reporter_filter:
            params["reporter_filter"] = reporter_filter

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return PaginatedTasks.model_validate(result)

    def move_task(
        self,
        task_id: str,
        move_request: TaskMoveRequest,
        integration_name: str = None,
    ) -> Task:
        """
        Move task.

        Args:
            task_id: The ID of the Task
            move_request: The new move request
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/move"
        params = {
            "integration_name": integration_name,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params, json=move_request.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        integration_name: str = None,
    ) -> Task:
        """
        Update task status.

        Args:
            task_id: The ID of the Task
            status: The new task status
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/status/update"
        params = {
            "integration_name": integration_name,
            "status": status,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def update_task_details(
        self,
        task_id: str,
        task_update: TaskUpdate,
        integration_name: str = None,
    ) -> Task:
        """
        Update task details (Report, Assignee, Labels, StartDate, EndDate, Priority).

        Args:
            task_id: The ID of the Task
            task_update: The task details to update
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/details/update"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params, json=task_update.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def add_subtask(
        self,
        task_id: str,
        subtask_create: SubtaskCreate,
        integration_name: str = None,
    ) -> Task:
        """
        Add a subtask to a task.

        Args:
            task_id: The ID of the Task
            subtask_create: The subtask to create
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/subtask/add"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=subtask_create.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def delete_subtask(
        self,
        task_id: str,
        subtask_id: str,
        integration_name: str = None,
    ) -> Task:
        """
        Delete a subtask from a task.

        Args:
            task_id: The ID of the Task
            subtask_id: The ID of the Subtask
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/subtask/{subtask_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def toggle_subtask_completion(
        self,
        task_id: str,
        subtask_id: str,
        completed: bool,
        integration_name: str = None,
    ) -> Task:
        """
        Toggle subtask completion status.

        Args:
            task_id: The ID of the Task
            subtask_id: The ID of the Subtask
            completed: Toggle subtask completion status
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/subtask/{subtask_id}/toggle-completion"
        params = {
            "integration_name": integration_name,
            "completed": completed,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def add_comment(
        self,
        task_id: str,
        comment_create: CommentCreate,
        integration_name: str = None,
    ) -> Task:
        """
        Add a comment to a task.

        Args:
            task_id: The ID of the Task
            comment_create: The comment to create
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/comment/add"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=comment_create.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def delete_comment(
        self,
        task_id: str,
        comment_id: str,
        integration_name: str = None,
    ) -> Task:
        """
        Delete a comment from a task.

        Args:
            task_id: The ID of the Task
            comment_id: The ID of the Comment
            integration_name: The name of the Integration

        Returns:
            Updated task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/comment/{comment_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def get_task_by_id(
        self,
        task_id: str,
        integration_name: str = None,
    ) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: The ID of the Task
            integration_name: The name of the Integration

        Returns:
            Task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return None

        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result) if result else None

    def create_task(
        self,
        task_create: TaskCreate,
        integration_name: str = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            task_create: The task to create
            integration_name: The name of the Integration

        Returns:
            Created task object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        payload = task_create.model_dump()
        json_payload = json.dumps(payload, default=custom_json_serializer_datetime)
        response = self.client.session.post(url, headers=headers, params=params, data=json_payload)
        result = self.client._handle_response(response=response, error_callable=raise_for_task_detail)
        return Task.model_validate(result)

    def delete_task(
        self,
        task_id: str,
        integration_name: str = None,
    ) -> None:
        """
        Delete a task.

        Args:
            task_id: The ID of the Task
            integration_name: The name of the Integration
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/task/{task_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_task_detail)
