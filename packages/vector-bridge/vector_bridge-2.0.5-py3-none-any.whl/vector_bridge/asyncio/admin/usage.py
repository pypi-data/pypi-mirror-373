from typing import Optional

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.usage import raise_for_usage_detail
from vector_bridge.schema.usage import PaginatedRequestUsages


class AsyncUsageAdmin:
    """Async admin client for usage endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def list_usage(
        self,
        primary_key: str,
        integration_name: str = None,
        limit: int = 25,
        last_evaluated_key: Optional[str] = None,
    ) -> PaginatedRequestUsages:
        """
        List usage with optional filters and pagination.

        Args:
            primary_key: Filter usage by organization ID, integration ID or API key hash
            integration_name: The name of the Integration
            limit: Number of usage records to return
            last_evaluated_key: Last evaluated key for pagination

        Returns:
            PaginatedRequestUsages with usage records and pagination information
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/usage"
        params = {
            "primary_key": primary_key,
            "integration_name": integration_name,
            "limit": limit,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_usage_detail)
            return PaginatedRequestUsages.model_validate(result)
