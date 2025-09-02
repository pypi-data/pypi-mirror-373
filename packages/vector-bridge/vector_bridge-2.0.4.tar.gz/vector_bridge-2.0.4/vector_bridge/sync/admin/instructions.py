from typing import List, Optional, Union

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.instructions import \
    raise_for_instruction_detail
from vector_bridge.schema.helpers.enums import OpenAIKey, PromptKey
from vector_bridge.schema.instruction import (AgentCreate, Instruction,
                                              InstructionCreate,
                                              PaginatedInstructions,
                                              Subordinate)


class InstructionsAdmin:
    """Admin client for instructions management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def add_instruction(self, instruction_data: InstructionCreate, integration_name: str = None) -> Instruction:
        """
        Add new Instruction to the integration.

        Args:
            instruction_data: Instruction details
            integration_name: The name of the Integration

        Returns:
            Created instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=instruction_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def get_instruction_by_name(self, instruction_name: str, integration_name: str = None) -> Optional[Instruction]:
        """
        Get the Instruction by name.

        Args:
            instruction_name: The name of the Instruction
            integration_name: The name of the Integration

        Returns:
            Instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction"
        params = {
            "integration_name": integration_name,
            "instruction_name": instruction_name,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return None

        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result) if result else None

    def get_instruction_by_id(self, instruction_id: str, integration_name: str = None) -> Optional[Instruction]:
        """
        Get the Instruction by ID.

        Args:
            instruction_id: The ID of the Instruction
            integration_name: The name of the Integration

        Returns:
            Instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return None

        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result) if result else None

    def list_instructions(
        self,
        integration_name: str = None,
        limit: int = 10,
        last_evaluated_key: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> PaginatedInstructions:
        """
        List Instructions for an Integration, sorted by created_at or updated_at.

        Args:
            integration_name: The name of the Integration
            limit: The number of Instructions to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: The sort field (created_at or updated_at)

        Returns:
            PaginatedInstructions with instructions and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instructions/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "sort_by": sort_by,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return PaginatedInstructions.model_validate(result)

    def delete_instruction(self, instruction_id: str, integration_name: str = None) -> None:
        """
        Delete Instruction from the integration.

        Args:
            instruction_id: The instruction ID
            integration_name: The name of the Integration
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)

    def add_agent(self, instruction_id: str, agent_data: AgentCreate, integration_name: str = None) -> Instruction:
        """
        Add new Agent to an Instruction.

        Args:
            instruction_id: The ID of the Instruction
            agent_data: Agent details to create
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/add"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params, json=agent_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def remove_agent(self, instruction_id: str, agent_name: str, integration_name: str = None) -> Instruction:
        """
        Remove Agent from an Instruction.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent to remove
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/remove"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def add_subordinate_to_agent(
        self,
        instruction_id: str,
        agent_name: str,
        subordinate_data: Subordinate,
        integration_name: str = None,
    ) -> Instruction:
        """
        Add new Subordinate to an Agent.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            subordinate_data: Subordinate details to add
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/subordinate/add"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params, json=subordinate_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def update_subordinate_delegate_decision(
        self,
        instruction_id: str,
        agent_name: str,
        subordinate_name: str,
        delegation_decision: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Set delegate decision for a subordinate.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            subordinate_name: The name of the Subordinate
            delegation_decision: The decision to delegate
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/subordinate/{subordinate_name}/update-delegate-decision"
        params = {
            "integration_name": integration_name,
            "delegation_decision": delegation_decision,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def remove_subordinate_from_agent(
        self,
        instruction_id: str,
        agent_name: str,
        subordinate_name: str,
        integration_name: str = None,
    ) -> None:
        """
        Remove Subordinate from Agent.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            subordinate_name: The name of the Subordinate Agent
            integration_name: The name of the Integration
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/subordinate/{subordinate_name}/remove"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)

    def update_agents_functions(
        self,
        instruction_id: str,
        agent_name: str,
        function_names: List[str],
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Agent's functions.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            function_names: The function names that agent should have access to
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/functions/update"
        params = {
            "integration_name": integration_name,
            "function_names": function_names,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def update_agents_prompt(
        self,
        instruction_id: str,
        agent_name: str,
        prompt_key: PromptKey,
        prompt_value: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Agent's prompt.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            prompt_key: The prompt key
            prompt_value: The prompt value
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/prompt/update"
        params = {"integration_name": integration_name, "prompt_key": prompt_key}
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params, json=prompt_value)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def update_agents_model(
        self,
        instruction_id: str,
        agent_name: str,
        model_alias: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Agent's model alias.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            model_alias: The model alias value
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/model/update"
        params = {
            "integration_name": integration_name,
            "model_alias": model_alias,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def update_instruction_ai(
        self,
        instruction_id: str,
        model_alias: str,
        ai_key: OpenAIKey,
        ai_value: Union[str, float, int],
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Instruction AI settings.

        Args:
            instruction_id: The ID of the Instruction
            model_alias: The model_alias value
            ai_key: The AI key
            ai_value: The value to set
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/ai/update"
        params = {
            "integration_name": integration_name,
            "model_alias": model_alias,
            "ai_key": ai_key,
            "ai_value": ai_value,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def add_ai_config(
        self,
        instruction_id: str,
        model: str,
        model_alias: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Add AI Config.

        Args:
            instruction_id: The ID of the Instruction
            model: Config model
            model_alias: The model alias value
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/ai/add-config"
        params = {
            "integration_name": integration_name,
            "model": model,
            "model_alias": model_alias,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def remove_ai_config(self, instruction_id: str, model_alias: str, integration_name: str = None) -> Instruction:
        """
        Remove AI Config.

        Args:
            instruction_id: The ID of the Instruction
            model_alias: Config model alias
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/ai/remove-config"
        params = {"integration_name": integration_name, "model_alias": model_alias}
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def set_instruction_api_key(
        self,
        instruction_id: str,
        ai_api_key: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Instruction API key.

        Args:
            instruction_id: The ID of the Instruction
            ai_api_key: The API key
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/ai/set-api-key"
        params = {
            "integration_name": integration_name,
            "ai_api_key": ai_api_key,
        }
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def update_instruction_debug(self, instruction_id: str, debug: bool, integration_name: str = None) -> Instruction:
        """
        Update Instruction debug switch.

        Args:
            instruction_id: The ID of the Instruction
            debug: The AI interactions debug switch
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/debug/update"
        params = {"integration_name": integration_name, "debug": debug}
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def update_instruction_max_turns(
        self, instruction_id: str, max_turns: int, integration_name: str = None
    ) -> Instruction:
        """
        Update Instruction max turns.

        Args:
            instruction_id: The ID of the Instruction
            max_turns: The maximum number of turns
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/max_turns/update"
        params = {"integration_name": integration_name, "max_turns": max_turns}
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)

    def update_instruction_default_ai_model(
        self,
        instruction_id: str,
        model_alias: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Instruction default AI model alias.

        Args:
            instruction_id: The ID of the Instruction
            model_alias: The AI model alias
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/ai/default-model"
        params = {"integration_name": integration_name, "model_alias": model_alias}
        headers = self.client._get_auth_headers()
        response = self.client.session.patch(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
        return Instruction.model_validate(result)
