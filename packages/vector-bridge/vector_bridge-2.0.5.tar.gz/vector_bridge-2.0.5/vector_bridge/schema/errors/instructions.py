from enum import Enum
from typing import Type


class InstructionError(Exception):
    """Base class for Instruction-related errors."""


class AgentAlreadyExists(InstructionError):
    """Raised when an agent with the given name already exists."""


class AgentDoesNotExist(InstructionError):
    """Raised when an agent with the given name does not exist."""


class AgentIsSubordinate(InstructionError):
    """Raised when an agent is subordinate to other agents."""


class SubordinateDoesNotExist(InstructionError):
    """Raised when a subordinate with the given name does not exist."""


class SubordinateAlreadyExists(InstructionError):
    """Raised when a subordinate with the given name already exists."""


class AgentNotFound(InstructionError):
    """Raised when the agent was not found."""


class SubordinateNotFound(InstructionError):
    """Raised when the subordinate was not found."""


class DefaultInstructionDeletionNotAllowed(InstructionError):
    """Raised when a default instruction cannot be deleted."""


class InstructionAlreadyExistsForIntegration(InstructionError):
    """Raised when an instruction already exists for this integration."""


class InstructionNotCreated(InstructionError):
    """Raised when an instruction was not created."""


class InstructionNotFound(InstructionError):
    """Raised when an instruction was not found."""


class InstructionGenericError(InstructionError):
    """Raised for unspecified instruction-related errors."""


class ModelConfigDoesNotExist(InstructionError):
    """Raised for unspecified instruction-related errors."""


class InstructionErrorDetail(str, Enum):
    AGENT_ALREADY_EXISTS = "Agent with the following name already exists"
    AGENT_DOES_NOT_EXIST = "Agent with the following name does not exist"
    AGENT_IS_SUBORDINATE = "Agent with the following name is subordinate to other agents"
    SUBORDINATE_DOES_NOT_EXIST = "Subordinate with the following name does not exist"
    SUBORDINATE_ALREADY_EXISTS = "Subordinate with the following name already exists"
    AGENT_NOT_FOUND = "Agent not found"
    SUBORDINATE_NOT_FOUND = "Subordinate not found"
    DEFAULT_DELETION_NOT_ALLOWED = "Default instruction can not be deleted"
    ALREADY_EXISTS_FOR_INTEGRATION = "Instruction with this ID already exists for this integration"
    NOT_CREATED = "Instruction was not created"
    NOT_FOUND = "Instruction not found"
    GENERIC_ERROR = "Something went wrong. Try again later"
    MODEL_CONFIG_DOES_NOT_EXIST = "Model config does not exist"

    def to_exception(self) -> Type[InstructionError]:
        """Return the exception class that corresponds to this instruction error detail."""
        mapping = {
            InstructionErrorDetail.AGENT_ALREADY_EXISTS: AgentAlreadyExists,
            InstructionErrorDetail.AGENT_DOES_NOT_EXIST: AgentDoesNotExist,
            InstructionErrorDetail.AGENT_IS_SUBORDINATE: AgentIsSubordinate,
            InstructionErrorDetail.SUBORDINATE_DOES_NOT_EXIST: SubordinateDoesNotExist,
            InstructionErrorDetail.SUBORDINATE_ALREADY_EXISTS: SubordinateAlreadyExists,
            InstructionErrorDetail.AGENT_NOT_FOUND: AgentNotFound,
            InstructionErrorDetail.SUBORDINATE_NOT_FOUND: SubordinateNotFound,
            InstructionErrorDetail.DEFAULT_DELETION_NOT_ALLOWED: DefaultInstructionDeletionNotAllowed,
            InstructionErrorDetail.ALREADY_EXISTS_FOR_INTEGRATION: InstructionAlreadyExistsForIntegration,
            InstructionErrorDetail.NOT_CREATED: InstructionNotCreated,
            InstructionErrorDetail.NOT_FOUND: InstructionNotFound,
            InstructionErrorDetail.GENERIC_ERROR: InstructionGenericError,
            InstructionErrorDetail.MODEL_CONFIG_DOES_NOT_EXIST: ModelConfigDoesNotExist,
        }
        return mapping[self]


def raise_for_instruction_detail(detail: str) -> None:
    """
    Raises the corresponding InstructionError based on the given instruction error detail string.
    """
    try:
        detail_enum = InstructionErrorDetail(detail)
    except ValueError:
        raise InstructionError(f"Unknown Instruction error: {detail}")
    raise detail_enum.to_exception()(detail)
