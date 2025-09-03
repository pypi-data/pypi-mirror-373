import json
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

import aiohttp
from pydantic import BaseModel, ConfigDict, Field

from vector_bridge.schema.helpers.enums import MessageType, UserType


class Meta(BaseModel):
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    function_calls: List[Any] = Field(default_factory=list)  # "ToolCallKwargs"
    function_responses: List[Any] = Field(default_factory=list)  # "ToolResponseMessage"


class MessageBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    integration_id: str
    chat_created_by: str
    timestamp: datetime
    message_created_by: str
    message_creator_type: UserType
    message_type: MessageType
    content: str
    deleted: bool = False


class MessageInDB(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    message_id: str
    data: Optional[Dict]
    meta: Meta

    @property
    def uuid(self):
        return self.message_id


class VectorAdditionalData(BaseModel):
    distance: Optional[float] = None


class VectorMessageInDB(MessageInDB):
    model_config = ConfigDict(from_attributes=True)

    additional: Optional[VectorAdditionalData] = Field(default=None)


class MessagesList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    messages: List[Union[MessageInDB, VectorMessageInDB]]
    limit: int
    offset: Optional[int]
    last_evaluated_key: Optional[str]
    has_more: bool


class MessagesListVectorDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    messages: List[Union[MessageInDB, VectorMessageInDB]]
    limit: int
    offset: Optional[int]
    has_more: bool


class MessagesListDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    messages: List[Union[MessageInDB, VectorMessageInDB]]
    limit: int
    last_evaluated_key: Optional[str]
    has_more: bool


class StreamingResponseError(Exception):
    """Custom exception for API errors."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(f"API Error {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class StreamingResponse:
    """
    Handles streaming response from the API with dual interface for chunks and final message.

    This class provides two main properties:
    - chunks: an iterator yielding each text chunk as it arrives
    - message: the final complete message object (waits for completion if needed)
    """

    def __init__(self, response):
        self._response = response
        self._chunks = []
        self._message = None
        self._fully_consumed = False

    @property
    def chunks(self) -> Iterator[str]:
        """
        Iterator over streaming text chunks.

        Yields:
            Text chunks as they arrive from the API.
        """
        # Return already processed chunks first
        for chunk in self._chunks:
            yield chunk

        # Process new chunks if not fully consumed
        if not self._fully_consumed:
            in_stream = False
            in_message = False
            message_json = ""

            for line in self._response.iter_lines():
                if not line:
                    continue

                decoded_line = line.decode("utf-8")

                # Handle stream section
                if decoded_line.strip() == "<stream>":
                    in_stream = True
                    continue

                if decoded_line.strip() == "</stream>":
                    in_stream = False
                    continue

                # Handle message section
                if decoded_line.strip() == "<message>":
                    in_message = True
                    continue

                if decoded_line.strip() == "</message>":
                    in_message = False
                    # Process the complete message
                    try:
                        self._message = MessageInDB.model_validate(json.loads(message_json))
                    except json.JSONDecodeError:
                        pass
                        # self._message = MessageInDB({"content": message_json, "error": "Failed to parse message"})
                    self._fully_consumed = True
                    break

                # Process content based on current section
                if in_stream:
                    # Check if chunk contains an error message
                    try:
                        error_data = json.loads(decoded_line)
                        if "status_code" in error_data and "detail" in error_data:
                            raise StreamingResponseError(error_data["status_code"], error_data["detail"])
                    except (json.JSONDecodeError, TypeError):
                        pass  # Not an error JSON, continue processing normally

                    self._chunks.append(decoded_line)
                    yield decoded_line
                elif in_message:
                    message_json += decoded_line

            self._fully_consumed = True

    @property
    def message(self) -> MessageInDB:
        """
        Get the final message, waiting for completion if necessary.

        Returns:
            The final complete message as MessageInDB object
        """
        if self._message is None and not self._fully_consumed:
            # Consume all chunks to get to the message
            for _ in self.chunks:
                if self._message is not None:
                    break

        return self._message


class AsyncStreamingResponseError(Exception):
    """Custom exception for API errors."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(f"API Error {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class AsyncStreamingResponse:
    """
    Handles async streaming response from the API with dual interface for chunks and final message.

    This class provides two main properties:
    - chunks: an async iterator yielding each text chunk as it arrives
    - message: the final complete message object (waits for completion if needed)
    """

    def __init__(self, response: aiohttp.ClientResponse):
        self._response = response
        self._chunks = []
        self._message = None
        self._fully_consumed = False

    async def chunks(self) -> AsyncIterator[str]:
        """
        Async iterator over streaming text chunks.

        Yields:
            Text chunks as they arrive from the API.
        """
        # Return already processed chunks first
        for chunk in self._chunks:
            yield chunk

        # Process new chunks if not fully consumed
        if not self._fully_consumed:
            in_stream = False
            in_message = False
            message_json = ""

            async for line in self._response.content:
                if not line:
                    continue

                decoded_line = line.decode("utf-8").rstrip("\n\r")

                if not decoded_line:
                    continue

                # Handle stream section
                if decoded_line.strip() == "<stream>":
                    in_stream = True
                    continue

                if decoded_line.strip() == "</stream>":
                    in_stream = False
                    continue

                # Handle message section
                if decoded_line.strip() == "<message>":
                    in_message = True
                    continue

                if decoded_line.strip() == "</message>":
                    in_message = False
                    # Process the complete message
                    try:
                        self._message = MessageInDB.model_validate(json.loads(message_json))
                    except json.JSONDecodeError:
                        pass
                        # self._message = MessageInDB({"content": message_json, "error": "Failed to parse message"})
                    self._fully_consumed = True
                    break

                # Process content based on current section
                if in_stream:
                    # Check if chunk contains an error message
                    try:
                        error_data = json.loads(decoded_line)
                        if "status_code" in error_data and "detail" in error_data:
                            raise AsyncStreamingResponseError(error_data["status_code"], error_data["detail"])
                    except (json.JSONDecodeError, TypeError):
                        pass  # Not an error JSON, continue processing normally

                    self._chunks.append(decoded_line)
                    yield decoded_line
                elif in_message:
                    message_json += decoded_line

            self._fully_consumed = True

    async def get_message(self) -> MessageInDB:
        """
        Get the final message, waiting for completion if necessary.

        Returns:
            The final complete message as MessageInDB object
        """
        if self._message is None and not self._fully_consumed:
            # Consume all chunks to get to the message
            async for _ in self.chunks():
                if self._message is not None:
                    break

        return self._message

    # Alternative property-style access (requires Python 3.9+ for async properties)
    @property
    async def message(self) -> MessageInDB:
        """
        Get the final message as an async property.
        Note: This requires Python 3.9+ and special handling.
        """
        return await self.get_message()

    async def close(self):
        """Close the response connection."""
        self._response.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def __aiter__(self):
        """Make the class itself async iterable."""
        return self.chunks()
