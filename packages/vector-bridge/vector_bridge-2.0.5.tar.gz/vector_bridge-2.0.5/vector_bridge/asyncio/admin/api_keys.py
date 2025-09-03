from typing import List, Optional

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.api_keys import APIKey, APIKeyCreate
from vector_bridge.schema.errors.api_keys import raise_for_api_key_detail


class AsyncAPIKeysAdmin:
    """Async admin client for API keys management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def create_api_key(self, api_key_data: APIKeyCreate) -> APIKey:
        """
        Create a new API key for integrations.

        Args:
            api_key_data: Details for the API key to create

        Returns:
            Created API key
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/api_key/create"
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, json=api_key_data.model_dump()) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)
            return APIKey.model_validate(result)

    async def get_api_key(self, api_key: str) -> APIKey:
        """
        Retrieve details about a specific API key.

        Args:
            api_key: The API key

        Returns:
            API key details
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/api_key/{api_key}"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)
            return APIKey.model_validate(result)

    async def delete_api_key(self, api_key: str) -> None:
        """
        Delete an API key.

        Args:
            api_key: The API key to delete
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/api_key/{api_key}"
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers) as response:
            if response.status != 204:
                await self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)

    async def list_api_keys(self, integration_name: Optional[str] = None) -> List[APIKey]:
        """
        List all API keys.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of API keys
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/api_keys"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)
            return [APIKey.model_validate(result) for result in results]
