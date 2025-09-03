from typing import Any, Dict

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.ai_knowledge.schemaless import (AIKnowledge,
                                                          AIKnowledgeCreate,
                                                          AIKnowledgeList)
from vector_bridge.schema.errors.ai_knowledge import \
    raise_for_ai_knowledge_detail


class AsyncDatabaseAIKnowledgeAdmin:
    """Async admin client for AI Knowledge database management."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def process_content(
        self,
        content_data: AIKnowledgeCreate,
        schema_name: str,
        unique_identifier: str,
        integration_name: str = None,
        content_uniqueness_check: bool = True,
    ) -> AIKnowledge:
        """
        Process content for updating or inserting.

        Args:
            content_data: Content data
            schema_name: The name of the Vector DB Schema
            unique_identifier: The unique identifier of the content entity
            integration_name: The name of the Integration
            content_uniqueness_check: Check for content uniqueness

        Returns:
            Processed content object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai-knowledge/content/upsert"
        params = {
            "integration_name": integration_name,
            "content_uniqueness_check": str(content_uniqueness_check).lower(),
            "schema_name": schema_name,
            "unique_identifier": unique_identifier,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.post(
            url, headers=headers, params=params, json=content_data.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledge.model_validate(result)

    async def update_item(
        self,
        item_data: Dict[str, Any],
        schema_name: str,
        item_id: str,
        integration_name: str = None,
    ) -> None:
        """
        Update an item.

        Args:
            item_data: Item data to update
            schema_name: The name of the Vector DB Schema
            item_id: The ID of the content chunk
            integration_name: The name of the Integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai-knowledge/content/update_item"
        params = {
            "integration_name": integration_name,
            "schema_name": schema_name,
            "item_id": item_id,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=item_data) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)

    async def get_content(self, schema_name: str, unique_identifier: str, integration_name: str = None) -> AIKnowledge:
        """
        Get content by unique identifier.

        Args:
            schema_name: The name of the Vector DB Schema
            unique_identifier: The unique identifier of the content entity
            integration_name: The name of the Integration

        Returns:
            List of content objects
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai-knowledge/content"
        params = {
            "integration_name": integration_name,
            "schema_name": schema_name,
            "unique_identifier": unique_identifier,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            results = await self.client._handle_response(
                response=response, error_callable=raise_for_ai_knowledge_detail
            )
            result = results[0]
            return AIKnowledge.model_validate(result)

    async def get_content_list(
        self, filters: Dict[str, Any], schema_name: str, integration_name: str = None
    ) -> AIKnowledgeList:
        """
        Get a list of content.

        Args:
            filters: Content filters
            schema_name: The name of the Vector DB Schema
            integration_name: The name of the Integration

        Returns:
            Dict with content items and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai-knowledge/content/list"
        params = {"integration_name": integration_name, "schema_name": schema_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=filters) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
            return AIKnowledgeList.model_validate(result)

    async def delete_content(self, schema_name: str, unique_identifier: str, integration_name: str = None) -> None:
        """
        Delete content by unique identifier.

        Args:
            schema_name: The name of the Vector DB Schema
            unique_identifier: The unique identifier of the content entity
            integration_name: The name of the Integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/ai-knowledge/content/delete"
        params = {
            "integration_name": integration_name,
            "schema_name": schema_name,
            "unique_identifier": unique_identifier,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            if response.status != 204:
                await self.client._handle_response(response=response, error_callable=raise_for_ai_knowledge_detail)
