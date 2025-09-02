from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.organization import \
    raise_for_organization_detail
from vector_bridge.schema.organization import Organization


class AsyncOrganizationAdmin:
    """Async admin client for organization management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def get_my_organization(self) -> Organization:
        """
        Retrieve detailed information about the organization linked to the currently authenticated user's account.

        Returns:
            Organization details
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/organization/me"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_organization_detail)
            return Organization.model_validate(data)
