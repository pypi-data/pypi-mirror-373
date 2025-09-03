from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from vector_bridge import AsyncVectorBridgeClient, VectorBridgeClient
from vector_bridge.schema.helpers.enums import OpenAIKey, PromptKey

DEFAULT_INSTRUCTION = "default"
DEFAULT_AGENT = "default"
FORWARD_DIALOGUE_TO_AGENT = "forward_dialogue_to_agent"


class InstructionsSorting(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"


class InstructionType(str, Enum):
    text = "text"
    voice = "voice"


class Position(BaseModel):
    x: float
    y: float


class OpenAI(BaseModel):
    model: str
    model_alias: str
    max_tokens: int
    frequency_penalty: float
    presence_penalty: float
    temperature: float
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime


class AI(BaseModel):
    current_model_alias: str | None = None
    models: Dict[str, OpenAI] = {}
    api_key: str = Field(default="")

    @property
    def current_model_config(self) -> OpenAI | None:
        return self.models.get(self.current_model_alias)

    def get_model_config_by_alias(self, alias: str) -> OpenAI | None:
        return self.models.get(alias)


class Prompts(BaseModel):
    system_prompt: str
    message_prompt: str
    knowledge_prompt: str


class Subordinate(BaseModel):
    subordinate_name: str
    delegation_decision: str


class AgentCreate(BaseModel):
    agent_name: str
    model_alias: str


class Agent(BaseModel):
    agent_name: str
    model_alias: str | None
    prompts: Prompts
    functions: List[str]
    subordinates: Dict[str, Subordinate] = Field(default_factory=dict)
    tool_choice: Optional[str]
    position: Position

    def get_subordinate_by_name(self, name: str) -> Subordinate | None:
        return self.subordinates.get(name)

    def add_subordinate(
        self,
        client: VectorBridgeClient,
        instruction_id: str,
        subordinate_data: Subordinate,
    ) -> "Instruction":
        """Add new Subordinate to this Agent."""
        return client.admin.instructions.add_subordinate_to_agent(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            subordinate_data=subordinate_data,
        )

    async def a_add_subordinate(
        self,
        client: AsyncVectorBridgeClient,
        instruction_id: str,
        subordinate_data: Subordinate,
    ) -> "Instruction":
        """Add new Subordinate to this Agent."""
        return await client.admin.instructions.add_subordinate_to_agent(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            subordinate_data=subordinate_data,
        )

    def update_subordinate_delegate_decision(
        self,
        client: VectorBridgeClient,
        instruction_id: str,
        subordinate_name: str,
        delegation_decision: str,
    ) -> "Instruction":
        """Update delegate decision for a subordinate of this Agent."""
        return client.admin.instructions.update_subordinate_delegate_decision(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            subordinate_name=subordinate_name,
            delegation_decision=delegation_decision,
        )

    async def a_update_subordinate_delegate_decision(
        self,
        client: AsyncVectorBridgeClient,
        instruction_id: str,
        subordinate_name: str,
        delegation_decision: str,
    ) -> "Instruction":
        """Update delegate decision for a subordinate of this Agent."""
        return await client.admin.instructions.update_subordinate_delegate_decision(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            subordinate_name=subordinate_name,
            delegation_decision=delegation_decision,
        )

    def remove_subordinate(
        self,
        client: VectorBridgeClient,
        instruction_id: str,
        subordinate_name: str,
    ) -> None:
        """Remove Subordinate from this Agent."""
        client.admin.instructions.remove_subordinate_from_agent(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            subordinate_name=subordinate_name,
        )

    async def a_remove_subordinate(
        self,
        client: AsyncVectorBridgeClient,
        instruction_id: str,
        subordinate_name: str,
    ) -> None:
        """Remove Subordinate from this Agent."""
        await client.admin.instructions.remove_subordinate_from_agent(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            subordinate_name=subordinate_name,
        )

    def update_functions(
        self,
        client: VectorBridgeClient,
        instruction_id: str,
        function_names: List[str],
    ) -> "Instruction":
        """Update this Agent's functions."""
        return client.admin.instructions.update_agents_functions(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            function_names=function_names,
        )

    async def a_update_functions(
        self,
        client: AsyncVectorBridgeClient,
        instruction_id: str,
        function_names: List[str],
    ) -> "Instruction":
        """Update this Agent's functions."""
        return await client.admin.instructions.update_agents_functions(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            function_names=function_names,
        )

    def update_prompt(
        self,
        client: VectorBridgeClient,
        instruction_id: str,
        prompt_key: PromptKey,
        prompt_value: str,
    ) -> "Instruction":
        """Update this Agent's prompt."""
        return client.admin.instructions.update_agents_prompt(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            prompt_key=prompt_key,
            prompt_value=prompt_value,
        )

    async def a_update_prompt(
        self,
        client: AsyncVectorBridgeClient,
        instruction_id: str,
        prompt_key: PromptKey,
        prompt_value: str,
    ) -> "Instruction":
        """Update this Agent's prompt."""
        return await client.admin.instructions.update_agents_prompt(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            prompt_key=prompt_key,
            prompt_value=prompt_value,
        )

    def update_model(
        self,
        client: VectorBridgeClient,
        instruction_id: str,
        model_alias: str,
    ) -> "Instruction":
        """Update this Agent's model alias."""
        return client.admin.instructions.update_agents_model(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            model_alias=model_alias,
        )

    async def a_update_model(
        self,
        client: AsyncVectorBridgeClient,
        instruction_id: str,
        model_alias: str,
    ) -> "Instruction":
        """Update this Agent's model alias."""
        return await client.admin.instructions.update_agents_model(
            instruction_id=instruction_id,
            agent_name=self.agent_name,
            model_alias=model_alias,
        )


class AgentPosition(BaseModel):
    agent_name: str
    position: Position


class AgentPositions(BaseModel):
    agents: List[AgentPosition]


class InstructionCreate(BaseModel):
    instruction_name: str
    instruction_type: InstructionType = Field(default=InstructionType.text)
    description: str


class Instruction(BaseModel):
    integration_id: str
    instruction_id: str
    instruction_name: str
    instruction_type: InstructionType = Field(default=InstructionType.text)
    description: str = Field(default="")
    created_at: datetime = Field(default=None)
    created_by: str = Field(default="")
    updated_at: datetime = Field(default=None)
    updated_by: str = Field(default="")
    ai: AI
    agents: Dict[str, Agent]
    max_turns: int
    max_depth: int
    debug: bool

    @property
    def uuid(self):
        return self.instruction_id

    def get_agent_by_name(self, name: str) -> Agent | None:
        return self.agents.get(name)

    def get_system_prompt(self, agent_name: str = DEFAULT_AGENT) -> str | None:
        agent = self.get_agent_by_name(name=agent_name)
        if agent:
            return agent.prompts.system_prompt
        return None

    def get_message_prompt(self, agent_name: str = DEFAULT_AGENT) -> str | None:
        agent = self.get_agent_by_name(name=agent_name)
        if agent:
            return agent.prompts.message_prompt
        return None

    def get_knowledge_prompt(self, agent_name: str = DEFAULT_AGENT) -> str | None:
        agent = self.get_agent_by_name(name=agent_name)
        if agent:
            return agent.prompts.knowledge_prompt
        return None

    def delete(self, client: VectorBridgeClient) -> None:
        """Delete this instruction."""
        client.admin.instructions.delete_instruction(
            instruction_id=self.instruction_id,
        )

    async def a_delete(self, client: AsyncVectorBridgeClient) -> None:
        """Delete this instruction."""
        await client.admin.instructions.delete_instruction(
            instruction_id=self.instruction_id,
        )

    def add_agent(self, client: VectorBridgeClient, agent_data: "AgentCreate") -> "Instruction":
        """Add new Agent to this Instruction."""
        return client.admin.instructions.add_agent(
            instruction_id=self.instruction_id,
            agent_data=agent_data,
        )

    async def a_add_agent(self, client: AsyncVectorBridgeClient, agent_data: "AgentCreate") -> "Instruction":
        """Add new Agent to this Instruction."""
        return await client.admin.instructions.add_agent(
            instruction_id=self.instruction_id,
            agent_data=agent_data,
        )

    def remove_agent(self, client: VectorBridgeClient, agent_name: str) -> "Instruction":
        """Remove Agent from this Instruction."""
        return client.admin.instructions.remove_agent(
            instruction_id=self.instruction_id,
            agent_name=agent_name,
        )

    async def a_remove_agent(self, client: AsyncVectorBridgeClient, agent_name: str) -> "Instruction":
        """Remove Agent from this Instruction."""
        return await client.admin.instructions.remove_agent(
            instruction_id=self.instruction_id,
            agent_name=agent_name,
        )

    def update_ai(
        self,
        client: VectorBridgeClient,
        model_alias: str,
        ai_key: OpenAIKey,
        ai_value: Union[str, float, int],
    ) -> "Instruction":
        """Update AI settings for this Instruction."""
        return client.admin.instructions.update_instruction_ai(
            instruction_id=self.instruction_id,
            model_alias=model_alias,
            ai_key=ai_key,
            ai_value=ai_value,
        )

    async def a_update_ai(
        self,
        client: "AsyncVectorBridgeClient",
        model_alias: str,
        ai_key: OpenAIKey,
        ai_value: Union[str, float, int],
    ) -> "Instruction":
        """Update AI settings for this Instruction."""
        return await client.admin.instructions.update_instruction_ai(
            instruction_id=self.instruction_id,
            model_alias=model_alias,
            ai_key=ai_key,
            ai_value=ai_value,
        )

    def add_ai_config(self, client: VectorBridgeClient, model: str, model_alias: str) -> "Instruction":
        """Add AI Config to this Instruction."""
        return client.admin.instructions.add_ai_config(
            instruction_id=self.instruction_id,
            model=model,
            model_alias=model_alias,
        )

    async def a_add_ai_config(self, client: AsyncVectorBridgeClient, model: str, model_alias: str) -> "Instruction":
        """Add AI Config to this Instruction."""
        return await client.admin.instructions.add_ai_config(
            instruction_id=self.instruction_id,
            model=model,
            model_alias=model_alias,
        )

    def remove_ai_config(self, client: VectorBridgeClient, model_alias: str) -> "Instruction":
        """Remove AI Config from this Instruction."""
        return client.admin.instructions.remove_ai_config(
            instruction_id=self.instruction_id,
            model_alias=model_alias,
        )

    async def a_remove_ai_config(self, client: AsyncVectorBridgeClient, model_alias: str) -> "Instruction":
        """Remove AI Config from this Instruction."""
        return await client.admin.instructions.remove_ai_config(
            instruction_id=self.instruction_id,
            model_alias=model_alias,
        )

    def set_api_key(self, client: VectorBridgeClient, ai_api_key: str) -> "Instruction":
        """Update API key for this Instruction."""
        return client.admin.instructions.set_instruction_api_key(
            instruction_id=self.instruction_id,
            ai_api_key=ai_api_key,
        )

    async def a_set_api_key(self, client: AsyncVectorBridgeClient, ai_api_key: str) -> "Instruction":
        """Update API key for this Instruction."""
        return await client.admin.instructions.set_instruction_api_key(
            instruction_id=self.instruction_id,
            ai_api_key=ai_api_key,
        )

    def update_debug(self, client: VectorBridgeClient, debug: bool) -> "Instruction":
        """Update debug switch for this Instruction."""
        return client.admin.instructions.update_instruction_debug(
            instruction_id=self.instruction_id,
            debug=debug,
        )

    async def a_update_debug(self, client: AsyncVectorBridgeClient, debug: bool) -> "Instruction":
        """Update debug switch for this Instruction."""
        return await client.admin.instructions.update_instruction_debug(
            instruction_id=self.instruction_id,
            debug=debug,
        )

    def update_max_turns(self, client: VectorBridgeClient, max_turns: int) -> "Instruction":
        """Update max turns for this Instruction."""
        return client.admin.instructions.update_instruction_max_turns(
            instruction_id=self.instruction_id,
            max_turns=max_turns,
        )

    async def a_update_max_turns(self, client: AsyncVectorBridgeClient, max_turns: int) -> "Instruction":
        """Update max turns for this Instruction."""
        return await client.admin.instructions.update_instruction_max_turns(
            instruction_id=self.instruction_id,
            max_turns=max_turns,
        )

    def update_default_ai_model(self, client: VectorBridgeClient, model_alias: str) -> "Instruction":
        """Update default AI model alias for this Instruction."""
        return client.admin.instructions.update_instruction_default_ai_model(
            instruction_id=self.instruction_id,
            model_alias=model_alias,
        )

    async def a_update_default_ai_model(self, client: AsyncVectorBridgeClient, model_alias: str) -> "Instruction":
        """Update default AI model alias for this Instruction."""
        return await client.admin.instructions.update_instruction_default_ai_model(
            instruction_id=self.instruction_id,
            model_alias=model_alias,
        )


class PaginatedInstructions(BaseModel):
    instructions: List[Instruction] = Field(default_factory=list)
    limit: int
    last_evaluated_key: Optional[str] = None
    has_more: bool = False
