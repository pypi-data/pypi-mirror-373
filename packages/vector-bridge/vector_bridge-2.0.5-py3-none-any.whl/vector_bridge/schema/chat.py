import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from vector_bridge.schema.helpers.enums import MessageStorageMode
from vector_bridge.schema.instruction import DEFAULT_AGENT


class ChatBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(default="")
    storage: MessageStorageMode
    agent: str = Field(default=DEFAULT_AGENT)
    core_knowledge: dict = Field(default_factory=dict)


class ChatCreate(ChatBase):
    model_config = ConfigDict(from_attributes=True)

    integration_id: str


class ChatInDB(ChatBase):
    model_config = ConfigDict(from_attributes=True)

    chat_id: str
    integration_id: str
    chat_created_by: str
    timestamp: datetime
    latest_message_timestamp: datetime
    deleted: bool = False

    @model_validator(mode="before")
    def check_vector_schema(cls, values):
        values["chat_id"] = str(values["chat_id"])
        values["integration_id"] = str(values["integration_id"])
        if "core_knowledge" in values and isinstance(values["core_knowledge"], str):
            values["core_knowledge"] = json.loads(values["core_knowledge"])
        return values

    @property
    def uuid(self):
        return self.chat_id


class Chat(ChatBase):
    model_config = ConfigDict(from_attributes=True)

    integration_id: str
    timestamp: datetime
    chat_created_by: str
    latest_message_timestamp: datetime

    @model_validator(mode="before")
    def check_vector_schema(cls, values):
        if isinstance(values, (Chat, ChatInDB)):
            return values

        values["integration_id"] = str(values["integration_id"])
        if "core_knowledge" in values and isinstance(values["core_knowledge"], str):
            values["core_knowledge"] = json.loads(values["core_knowledge"])
        return values


class ChatsList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chats: List[Chat]
    limit: int
    offset: int = Field(default=0)
    has_more: bool = Field(default=False)


class ChatFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)
