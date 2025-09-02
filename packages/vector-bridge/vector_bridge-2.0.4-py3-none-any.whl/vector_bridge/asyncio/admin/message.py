from typing import Optional

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.message import raise_for_message_detail
from vector_bridge.schema.messages import MessagesListDB, MessagesListVectorDB


class AsyncMessageAdmin:
    """Async admin client for message management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def fetch_internal_messages_from_vector_db(
        self,
        suffix: str,
        integration_name: str = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: str = "asc",
        near_text: Optional[str] = None,
    ) -> MessagesListVectorDB:
        """
        Retrieve internal messages from vector database.

        Args:
            suffix: Suffix for the user_id
            integration_name: The name of the integration
            limit: Number of messages to return
            offset: Starting point for fetching records
            sort_order: Order to sort results (asc/desc)
            near_text: Text to search for semantically similar messages

        Returns:
            MessagesListVectorDB with messages and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai/internal-messages/weaviate"
        params = {
            "suffix": suffix,
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order,
        }
        if near_text:
            params["near_text"] = near_text

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_message_detail)
            return MessagesListVectorDB.model_validate(result)

    async def fetch_internal_messages_from_db(
        self,
        suffix: str,
        integration_name: str = None,
        limit: int = 50,
        last_evaluated_key: Optional[str] = None,
        sort_order: str = "asc",
        crypto_key: Optional[str] = None,
    ) -> MessagesListDB:
        """
        Retrieve internal messages from DB.

        Args:
            suffix: Suffix for the user_id
            integration_name: The name of the integration
            limit: Number of messages to return
            last_evaluated_key: Key for pagination
            sort_order: Order to sort results (asc/desc)
            crypto_key: Crypto key for decryption

        Returns:
            MessagesListDB with messages and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai/internal-messages/dynamo-db"
        params = {
            "suffix": suffix,
            "integration_name": integration_name,
            "limit": limit,
            "sort_order": sort_order,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        if crypto_key:
            headers["Crypto-Key"] = crypto_key

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_message_detail)
            return MessagesListDB.model_validate(result)
