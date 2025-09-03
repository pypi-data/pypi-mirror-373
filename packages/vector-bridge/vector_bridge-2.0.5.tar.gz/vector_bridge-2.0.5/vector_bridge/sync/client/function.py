import json
from typing import Any, Dict

from pydantic import BaseModel

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.functions import raise_for_function_detail


class FunctionClient:
    """User client for function endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def run_function(
        self,
        function_name: str,
        function_args: Dict[str, Any],
        integration_name: str = None,
        instruction_name: str = "default",
        agent_name: str = "default",
    ) -> Any:
        """
        Run a function.

        Args:
            function_name: The name of the function to run
            function_args: Arguments to pass to the function
            integration_name: The name of the Integration
            instruction_name: The name of the instruction
            agent_name: The name of the agent

        Returns:
            Function execution result
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        response_format = function_args.get("response_format")
        if isinstance(response_format, type) and issubclass(response_format, BaseModel):
            function_args["response_format"] = response_format.model_json_schema()

        url = f"{self.client.base_url}/v1/function/{function_name}/run"
        params = {
            "integration_name": integration_name,
            "instruction_name": instruction_name,
            "agent_name": agent_name,
        }

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=function_args, stream=True)
        if response.status_code >= 400:
            self.client._handle_response(response=response, error_callable=raise_for_function_detail)

        text = response.text
        try:
            return json.loads(text)
        except json.decoder.JSONDecodeError:
            return text
