from typing import Any, Dict

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.chat import Chat
from vector_bridge.schema.errors.chat import raise_for_chat_detail


class AIClient:
    """User client for AI endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def set_current_agent(
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
            api_key: API key for authentication
            integration_name: The name of the Integration
            instruction_name: The name of the instruction

        Returns:
            Chat object
        """
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
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
        return Chat.model_validate(result)

    def set_core_knowledge(self, user_id: str, core_knowledge: Dict[str, Any], integration_name: str = None) -> Chat:
        """
        Set the core knowledge.

        Args:
            user_id: User ID
            core_knowledge: The core knowledge to set
            integration_name: The name of the Integration

        Returns:
            Chat object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai/core-knowledge/set"
        params = {"user_id": user_id, "integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params, json=core_knowledge)
        result = self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
        return Chat.model_validate(result)
