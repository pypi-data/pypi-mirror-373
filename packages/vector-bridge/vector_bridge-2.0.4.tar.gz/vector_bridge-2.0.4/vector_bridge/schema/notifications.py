from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class NotificationStatus(str, Enum):
    sent = "sent"


class NotificationState(BaseModel):
    status: NotificationStatus
    channel: str


class NotificationTypes(str, Enum):
    chat = "CHAT"
    file = "FILE"
    tags = "TAGS"


class NotificationSubTypes(str, Enum):
    chat_history_update = "CHAT_HISTORY_UPDATE"
    internal_chat_response = "INTERNAL_CHAT_RESPONSE"


class NotificationTitles(str, Enum):
    new_message = "sent a message"
    add_file = "added a file"
    delete_file = "deleted a file"
    add_tags_to_file = "added tags to a file"
    removed_tags_to_file = "removed tags from a file"


class NotificationInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    integration_id: str
    title: Optional[str] = None
    type: NotificationTypes
    subtype: NotificationSubTypes
    created_by: str
    created_by_full_name: Optional[str] = Field(default="Noname")
    created_at: datetime
    expire_at: int
    data: Dict

    @property
    def uuid(self):
        return self.id


class Notification(NotificationInDB):
    pass


class NotificationsList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notifications: List[Notification]
    limit: int
    last_evaluated_key: Optional[str] = Field(default=None)
