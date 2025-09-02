from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.message import raise_for_message_detail
from vector_bridge.schema.helpers.enums import SortOrder
from vector_bridge.schema.messages import (MessagesListDB,
                                           MessagesListVectorDB,
                                           StreamingResponse)


class AIMessageClient:
    """User client for message endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def process_message_stream(
        self,
        content: str,
        chat_id: str,
        message_id: int = None,
        integration_name: str = None,
        instruction_name: str = "default",
        function_to_call: Optional[str] = None,
        max_turns: Optional[int] = None,
        max_depth: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        crypto_key: Optional[str] = None,
    ) -> StreamingResponse:
        """
        Process a message and get streaming AI response.

        Args:
            content: Message content
            chat_id: User ID (anything to identify a chat with a user)
            message_id: Message ID (anything to identify a message)
            integration_name: The name of the integration
            instruction_name: The name of the instruction
            function_to_call: Function to call (optional)
            max_turns: Max number of conversation turns within each Agent (optional)
            max_depth: Max allowed Agent delegation depth (optional)
            data: Additional data (optional)
            crypto_key: Crypto key for encrypted storage (optional)

        Returns:
            Stream of message objects including AI response
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/stream/ai/process-message/response-text"
        params = {
            "user_id": chat_id,
            "integration_name": integration_name,
            "instruction_name": instruction_name,
        }

        if message_id:
            params["message_id"] = message_id

        if function_to_call:
            params["function_to_call"] = function_to_call

        if max_turns:
            params["max_turns"] = max_turns

        if max_depth:
            params["max_depth"] = max_depth

        headers = self.client._get_auth_headers()
        if crypto_key:
            headers["Crypto-Key"] = crypto_key

        message_data = {"content": content}
        if data:
            message_data["data"] = data

        response = self.client.session.post(url, headers=headers, params=params, json=message_data, stream=True)
        if response.status_code >= 400:
            self.client._handle_response(
                response=response, error_callable=raise_for_message_detail
            )  # This should raise an appropriate exception

        return StreamingResponse(response)

    def process_message_json(
        self,
        content: str,
        response_model: BaseModel,
        chat_id: str,
        message_id: int = None,
        integration_name: str = None,
        instruction_name: str = "default",
        available_functions: Optional[List[str]] = None,
        function_to_call: Optional[str] = None,
        max_turns: Optional[int] = None,
        max_depth: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        crypto_key: Optional[str] = None,
    ) -> BaseModel:
        """
        Process a message and get AI response as structured JSON.

        Args:
            content: Message content
            response_model: Structure definition for the response
            chat_id: User ID (anything to identify a chat with a user)
            message_id: Message ID (anything to identify a message)
            integration_name: The name of the integration
            instruction_name: The name of the instruction
            available_functions: Override the functions accessible to AI
            function_to_call: Function to call (optional)
            max_turns: Max number of conversation turns within each Agent (optional)
            max_depth: Max allowed Agent delegation depth (optional)
            data: Additional data (optional)
            crypto_key: Crypto key for encrypted storage (optional)

        Returns:
            JSON response from AI
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai/process-message/response-json"
        params = {
            "user_id": chat_id,
            "integration_name": integration_name,
            "instruction_name": instruction_name,
        }

        if message_id:
            params["message_id"] = message_id

        if available_functions:
            params["available_functions"] = available_functions

        if function_to_call:
            params["function_to_call"] = function_to_call

        if max_turns:
            params["max_turns"] = max_turns

        if max_depth:
            params["max_depth"] = max_depth

        headers = self.client._get_auth_headers()
        if crypto_key:
            headers["Crypto-Key"] = crypto_key

        model_json_schema = response_model.model_json_schema()

        message_data = {
            "content": content,
            "response_structure_definition": model_json_schema,
        }
        if data:
            message_data["data"] = data

        response = self.client.session.post(url, headers=headers, params=params, json=message_data)
        result = self.client._handle_response(response=response, error_callable=raise_for_message_detail)
        return response_model.model_validate(result)

    def fetch_messages_from_vector_db(
        self,
        chat_id: str,
        integration_name: str = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = SortOrder.DESCENDING,
        near_text: Optional[str] = None,
    ) -> MessagesListVectorDB:
        """
        Retrieve messages from vector database.

        Args:
            chat_id: User ID or Chat ID
            integration_name: The name of the integration
            limit: Number of messages to return
            offset: Starting point for fetching records
            sort_order: Order to sort results (asc/desc)
            near_text: Text to search for semantically similar messages

        Returns:
            MessagesListVectorDB with messages and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai/messages/weaviate"
        params = {
            "user_id": chat_id,
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order.value,
        }
        if near_text:
            params["near_text"] = near_text

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_message_detail)
        return MessagesListVectorDB.model_validate(result)

    def fetch_messages_from_db(
        self,
        chat_id: str,
        integration_name: str = None,
        limit: int = 50,
        last_evaluated_key: Optional[str] = None,
        sort_order: SortOrder = SortOrder.DESCENDING,
        crypto_key: Optional[str] = None,
    ) -> MessagesListDB:
        """
        Retrieve messages from DB.

        Args:
            chat_id: User ID or Chat ID
            integration_name: The name of the integration
            limit: Number of messages to return
            last_evaluated_key: Key for pagination
            sort_order: Order to sort results (asc/desc)
            crypto_key: Crypto key for decryption

        Returns:
            Dict with messages and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/ai/messages/dynamo-db"
        params = {
            "user_id": chat_id,
            "integration_name": integration_name,
            "limit": limit,
            "sort_order": sort_order.value,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        if crypto_key:
            headers["Crypto-Key"] = crypto_key

        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_message_detail)
        return MessagesListDB.model_validate(result)
