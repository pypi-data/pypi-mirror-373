from enum import Enum
from typing import Type


class ChatError(Exception):
    """Base class for Chat-related errors."""


class AgentNotFound(ChatError):
    """Raised when the specified agent does not exist."""


class ChatNotFound(ChatError):
    """Raised when the specified chat does not exist."""


class ChatErrorDetail(str, Enum):
    AGENT_NOT_FOUND = "Agent with the following name does not exist"
    CHAT_NOT_FOUND = "The following Chat does not exist"

    def to_exception(self) -> Type[ChatError]:
        """Return the exception class that corresponds to this chat error detail."""
        mapping = {
            ChatErrorDetail.AGENT_NOT_FOUND: AgentNotFound,
            ChatErrorDetail.CHAT_NOT_FOUND: ChatNotFound,
        }
        return mapping[self]


def raise_for_chat_detail(detail: str) -> None:
    """
    Raises the corresponding ChatError based on the given chat error detail string.
    """
    try:
        detail_enum = ChatErrorDetail(detail)
    except ValueError:
        raise ChatError(f"Unknown Chat error: {detail}")
    raise detail_enum.to_exception()(detail)
