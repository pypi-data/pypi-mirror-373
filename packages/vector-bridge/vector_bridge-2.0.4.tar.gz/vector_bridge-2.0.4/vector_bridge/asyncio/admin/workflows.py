from datetime import datetime
from typing import Optional

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.workflows import raise_for_workflow_detail
from vector_bridge.schema.workflows import PaginatedWorkflows


class AsyncWorkflowsAdmin:
    """Async admin client for workflows management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def list_workflows(
        self,
        integration_name: str = None,
        workflow_name: str = None,
        limit: int = 25,
        last_evaluated_key: Optional[str] = None,
    ) -> PaginatedWorkflows:
        """
        List Workflows for an Integration, sorted by created_at or updated_at.

        Args:
            integration_name: The name of the Integration
            workflow_name: The name of the Workflow
            limit: The number of Workflows to retrieve
            last_evaluated_key: Pagination key for the next set of results

        Returns:
            PaginatedWorkflows with workflows and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/workflows/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
        }
        if workflow_name:
            params["workflow_name"] = workflow_name
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
            return PaginatedWorkflows.model_validate(result)

    async def delete_workflow(self, workflow_id: str, created_at: datetime, integration_name: str = None) -> None:
        """
        Delete Workflow from the integration.

        Args:
            workflow_id: The workflow ID
            integration_name: The name of the Integration
            created_at: The created at
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/workflows/{workflow_id}/delete"
        params = {
            "integration_name": integration_name,
            "created_at": created_at.isoformat(),
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_workflow_detail)
