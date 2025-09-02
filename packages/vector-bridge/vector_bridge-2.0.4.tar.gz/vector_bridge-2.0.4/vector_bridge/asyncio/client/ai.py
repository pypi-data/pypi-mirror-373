from typing import Any, Dict

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.chat import Chat
from vector_bridge.schema.errors.chat import raise_for_chat_detail


class AsyncAIClient:
    """Async user client for AI endpoints that require an API key."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def set_current_agent(
        self,
        user_id: str,
        agent_name: str,
        integration_name: str = None,
        instruction_name: str = "default",
    ) -> Chat:
        """
        Set the current agent.

        Args:
            user_id: User ID
            agent_name: The agent to set
            integration_name: The name of the Integration
            instruction_name: The name of the instruction

        Returns:
            Chat object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai/agent/set"
        params = {
            "user_id": user_id,
            "integration_name": integration_name,
            "instruction_name": instruction_name,
            "agent_name": agent_name,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return Chat.model_validate(result)

    async def set_core_knowledge(
        self, user_id: str, core_knowledge: Dict[str, Any], integration_name: str = None
    ) -> Chat:
        """
        Set the core knowledge.

        Args:
            user_id: User ID
            core_knowledge: The core knowledge to set
            integration_name: The name of the Integration

        Returns:
            Chat object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai/core-knowledge/set"
        params = {"user_id": user_id, "integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params, json=core_knowledge) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return Chat.model_validate(result)
