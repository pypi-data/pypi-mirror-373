from typing import Dict, List, Optional

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.integrations import \
    raise_for_integration_detail
from vector_bridge.schema.helpers.enums import MessageStorageMode, WeaviateKey
from vector_bridge.schema.integrations import Integration, IntegrationCreate
from vector_bridge.schema.user import UsersList


class AsyncIntegrationsAdmin:
    """Async admin client for integrations management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def get_integrations_list(self) -> List[Integration]:
        """
        Get a list of all integrations.

        Returns:
            List of integration objects
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integrations"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return [Integration.model_validate(item) for item in data]

    async def get_integration_by_id(self, integration_id: str) -> Optional[Integration]:
        """
        Get integration by ID.

        Args:
            integration_id: The integration ID

        Returns:
            Integration object
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/id/{integration_id}"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            if response.status in [403, 404]:
                return None

            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return Integration.model_validate(data)

    async def get_integration_by_name(self, integration_name: str = None) -> Optional[Integration]:
        """
        Get integration by name.

        Args:
            integration_name: The integration name

        Returns:
            Integration object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/name/{integration_name}"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            if response.status in [403, 404]:
                return None

            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return Integration.model_validate(data)

    async def add_integration(self, integration_data: IntegrationCreate) -> Integration:
        """
        Add a new integration.

        Args:
            integration_data: Integration details

        Returns:
            Created integration object
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/add"
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, json=integration_data.model_dump()) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return Integration.model_validate(data)

    async def delete_integration(self, integration_name: str = None) -> List[Integration]:
        """
        Delete an integration.

        Args:
            integration_name: The name of the integration to delete

        Returns:
            List of remaining integrations
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return [Integration.model_validate(item) for item in data]

    async def update_integration_weaviate(
        self,
        weaviate_key: WeaviateKey,
        weaviate_value: str,
        integration_name: str = None,
    ) -> Integration:
        """
        Update Integration weaviate settings.

        Args:
            weaviate_key: The Weaviate key
            weaviate_value: The Weaviate value
            integration_name: The name of the Integration

        Returns:
            Updated integration object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/edit/weaviate"
        params = {
            "integration_name": integration_name,
            "weaviate_key": weaviate_key.value,
            "weaviate_value": weaviate_value,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return Integration.model_validate(data)

    async def update_integration_published(self, published: bool, integration_name: str = None) -> Integration:
        """
        Update Integration published setting.

        Args:
            published: The published value
            integration_name: The name of the Integration

        Returns:
            Updated integration object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/edit/published"
        params = {
            "integration_name": integration_name,
            "published": str(published).lower(),
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return Integration.model_validate(data)

    async def update_message_storage_mode(
        self, message_storage_mode: MessageStorageMode, integration_name: str = None
    ) -> Integration:
        """
        Update Integration message storage mode setting.

        Args:
            message_storage_mode: The Message Storage Mode
            integration_name: The name of the Integration

        Returns:
            Updated integration object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/edit/message-storage-mode"
        params = {
            "integration_name": integration_name,
            "message_storage_mode": message_storage_mode.value,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return Integration.model_validate(data)

    async def update_environment_variables(
        self, env_variables: Dict[str, str], integration_name: str = None
    ) -> Integration:
        """
        Update Integration environment variables.

        Args:
            env_variables: The Environment Variables
            integration_name: The name of the Integration

        Returns:
            Updated integration object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/edit/environment-variables"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params, json=env_variables) as response:
            data = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return Integration.model_validate(data)

    async def add_user_to_integration(
        self,
        user_id: str,
        security_group_id: str,
        integration_name: str = None,
    ) -> UsersList:
        """
        Add user to the Integration by id.

        Args:
            integration_name: The integration name
            user_id: The user id
            security_group_id: The Security Group

        Returns:
            Users list
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/name/{integration_name}/add-user/{user_id}"
        params = {"security_group_id": security_group_id}
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return UsersList.model_validate(result)

    async def remove_user_from_integration(
        self,
        user_id: str,
        integration_name: str = None,
    ) -> UsersList:
        """
        Remove user from Integration.

        Args:
            integration_name: The integration name
            user_id: The user id

        Returns:
            Users list
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/name/{integration_name}/remove-user/{user_id}"
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return UsersList.model_validate(result)

    async def update_users_security_group(
        self,
        user_id: str,
        security_group_id: str,
        integration_name: str = None,
    ) -> UsersList:
        """
        Update user's security group in an integration.

        Args:
            integration_name: The integration name
            user_id: The user id
            security_group_id: The Security Group

        Returns:
            Users list
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = (
            f"{self.client.base_url}/v1/admin/integration/name/{integration_name}/update-users-security-group/{user_id}"
        )
        params = {"security_group_id": security_group_id}
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return UsersList.model_validate(result)

    async def get_users_from_integration(
        self,
        limit: int = 25,
        integration_name: str = None,
        last_evaluated_key: Optional[str] = None,
    ) -> UsersList:
        """
        Get users in an Integration by id.

        Args:
            integration_name: The integration name
            limit: Number of users to return
            last_evaluated_key: Last evaluated key for pagination

        Returns:
            Users list
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration/name/{integration_name}/users"
        params = {"limit": limit}
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return UsersList.model_validate(result)

    async def get_integration_names_of_a_user(self, user_id: str) -> List[str]:
        """
        Get integration names that a user belongs to.

        Args:
            user_id: The user id

        Returns:
            List of integration names
        """
        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/integration_names/user/id/{user_id}"
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_integration_detail)
            return result
