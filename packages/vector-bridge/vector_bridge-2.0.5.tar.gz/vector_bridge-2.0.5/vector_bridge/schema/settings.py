from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class DistributionType(str, Enum):
    SELF_HOSTED = "self_hosted"


class FilesConfig(BaseModel):
    max_size_bytes: int = Field(default=20000000)
    types: List[str]
    mime_types: Dict[str, List[str]]


class AIModelConfig(BaseModel):
    model: str
    max_tokens: int


class MinMax(BaseModel):
    min: float
    max: float


class OpenAIConfig(BaseModel):
    presence_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    frequency_penalty: MinMax = Field(default=MinMax(min=-2.0, max=2.0))
    temperature: MinMax = Field(default=MinMax(min=0.0, max=2.0))
    models: List[AIModelConfig] = Field(default=[])


class AIConfig(BaseModel):
    litellm: OpenAIConfig = Field(default=OpenAIConfig())


class Settings(BaseModel):
    files: FilesConfig
    ai: AIConfig
    distribution_type: DistributionType
