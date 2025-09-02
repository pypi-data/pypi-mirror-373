import json
from typing import Any, Dict

from pydantic import BaseModel

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.functions import raise_for_function_detail


class AsyncFunctionClient:
    """Async user client for function endpoints that require an API key."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def run_function(
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
        await self.client._ensure_session()

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

        async with self.client.session.post(url, headers=headers, params=params, json=function_args) as response:
            if response.status >= 400:
                await self.client._handle_response(response=response, error_callable=raise_for_function_detail)

            text = await response.text()
            try:
                return json.loads(text)
            except json.decoder.JSONDecodeError:
                return text
