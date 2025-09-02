from typing import Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.usage import raise_for_usage_detail
from vector_bridge.schema.usage import PaginatedRequestUsages


class UsageAdmin:
    """Admin client for usage endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def list_usage(
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
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_usage_detail)
        return PaginatedRequestUsages.model_validate(result)
