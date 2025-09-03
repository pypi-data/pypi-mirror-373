from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.chat import Chat, ChatsList
from vector_bridge.schema.errors.chat import raise_for_chat_detail


class AsyncChatAdmin:
    """Async admin client for chat management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def fetch_chats_for_my_organization(
        self, integration_name: str = None, limit: int = 50, offset: int = 0
    ) -> ChatsList:
        """
        Retrieve a list of chat sessions associated with the organization.

        Args:
            integration_name: The name of the integration
            limit: Number of chat records to return
            offset: Starting point for fetching records

        Returns:
            ChatsList with chats and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/chats"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return ChatsList.model_validate(result)

    async def fetch_my_chats(self, integration_name: str = None, limit: int = 50, offset: int = 0) -> ChatsList:
        """
        Retrieve a list of chat sessions for the current user.

        Args:
            integration_name: The name of the integration
            limit: Number of chat records to return
            offset: Starting point for fetching records

        Returns:
            ChatsList with chats and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/chats/me"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return ChatsList.model_validate(result)

    async def get_chat(self, chat_id: str, integration_name: str = None) -> ChatsList:
        """
        Retrieve a list of chat sessions for the current user.

        Args:
            chat_id: Chat ID
            integration_name: The name of the integration

        Returns:
            ChatsList with chats and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/chats/me"
        params = {
            "chat_id": chat_id,
            "integration_name": integration_name,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return ChatsList.model_validate(result)

    async def delete_chat(self, chat_id: str, integration_name: str = None) -> None:
        """
        Delete a chat session between the organization and a specific user.

        Args:
            chat_id: The unique identifier of the user
            integration_name: The name of the integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/chat/delete/{chat_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            if response.status != 204:
                await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)

    async def create_chat(self, chat_id: str, title: str = "New Chat", integration_name: str = None) -> Chat:
        """
        Create a new chat session between the organization and a specific user.

        Args:
            chat_id: Unique identifier of the user
            title: Title for the new chat
            integration_name: Name of the integration

        Returns:
            Chat: The newly created chat session
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/chat/create/{chat_id}"
        params = {
            "integration_name": integration_name,
            "title": title,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return Chat.model_validate(result)
