from typing import List, Optional

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.api_keys import APIKey, APIKeyCreate
from vector_bridge.schema.errors.api_keys import raise_for_api_key_detail


class APIKeysAdmin:
    """Admin client for API keys management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def create_api_key(self, api_key_data: APIKeyCreate) -> APIKey:
        """
        Create a new API key for integrations.

        Args:
            api_key_data: Details for the API key to create

        Returns:
            Created API key
        """
        url = f"{self.client.base_url}/v1/admin/api_key/create"
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, json=api_key_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)
        return APIKey.model_validate(result)

    def get_api_key(self, api_key: str) -> APIKey:
        """
        Retrieve details about a specific API key.

        Args:
            api_key: The API key

        Returns:
            API key details
        """
        url = f"{self.client.base_url}/v1/admin/api_key/{api_key}"
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers)
        result = self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)
        return APIKey.model_validate(result)

    def delete_api_key(self, api_key: str) -> None:
        """
        Delete an API key.

        Args:
            api_key: The API key to delete
        """
        url = f"{self.client.base_url}/v1/admin/api_key/{api_key}"
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers)
        if response.status_code != 204:
            self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)

    def list_api_keys(self, integration_name: Optional[str] = None) -> List[APIKey]:
        """
        List all API keys.

        Args:
            integration_name: Specifies the name of the integration module being queried

        Returns:
            List of API keys
        """
        url = f"{self.client.base_url}/v1/admin/api_keys"
        params = {}
        if integration_name:
            params["integration_name"] = integration_name

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        results = self.client._handle_response(response=response, error_callable=raise_for_api_key_detail)
        return [APIKey.model_validate(result) for result in results]
