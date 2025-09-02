from enum import Enum
from typing import Type


class MessageError(Exception):
    """Base class for Message-related errors."""


class MessageAlreadyExists(MessageError):
    """Raised when a message with this ID already exists."""


class MessageNotCreated(MessageError):
    """Raised when a message was not created."""


class MessageGenericError(MessageError):
    """Raised for unspecified message-related errors."""


class AgentDoesNotExistForMessage(MessageError):
    """Raised when the specified agent does not exist for a message."""


class ChatDoesNotExistForMessage(MessageError):
    """Raised when the specified chat does not exist for a message."""


class InvalidModel(MessageError):
    """Raised when an invalid model provided."""


class MessageErrorDetail(str, Enum):
    ALREADY_EXISTS = "Message with this ID already exists"
    NOT_CREATED = "Message was not created"
    GENERIC_ERROR = "Something went wrong. Try again later"
    AGENT_DOES_NOT_EXIST = "Agent with the following name does not exist"
    CHAT_DOES_NOT_EXIST = "The following Chat does not exist"
    INVALID_MODEL = "Invalid model provided"

    def to_exception(self) -> Type[MessageError]:
        """Return the exception class that corresponds to this message error detail."""
        mapping = {
            MessageErrorDetail.ALREADY_EXISTS: MessageAlreadyExists,
            MessageErrorDetail.NOT_CREATED: MessageNotCreated,
            MessageErrorDetail.GENERIC_ERROR: MessageGenericError,
            MessageErrorDetail.AGENT_DOES_NOT_EXIST: AgentDoesNotExistForMessage,
            MessageErrorDetail.CHAT_DOES_NOT_EXIST: ChatDoesNotExistForMessage,
            MessageErrorDetail.INVALID_MODEL: InvalidModel,
        }
        return mapping[self]


def raise_for_message_detail(detail: str) -> None:
    """
    Raises the corresponding MessageError based on the given message error detail string.
    """
    try:
        detail_enum = MessageErrorDetail(detail)
    except ValueError:
        raise MessageError(f"Unknown Message error: {detail}")
    raise detail_enum.to_exception()(detail)
