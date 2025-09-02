"""Models for LLM service."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """LLM provider options."""

    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"
    GOOGLE_VERTEXAI = "google_vertexai"


class CostConfig(BaseModel):
    """Cost configuration for LLM model."""

    input: float
    output: float


class LLMFeatures(BaseModel):
    """Features supported by LLM model."""

    streaming: Optional[bool] = True
    tools: Optional[bool] = True
    temperature: Optional[bool] = True
    parallel_tool_calls: Optional[bool] = True
    system_prompt: Optional[bool] = True
    max_tokens: Optional[bool] = True


class LLMModel(BaseModel):
    """LLM model configuration."""

    base_name: str
    deployment_name: str
    label: Optional[str] = None
    multimodal: Optional[bool] = None
    react_agent: Optional[bool] = None
    enabled: bool
    provider: Optional[LLMProvider] = None
    default: Optional[bool] = None
    cost: Optional[CostConfig] = None
    max_output_tokens: Optional[int] = None
    features: Optional[LLMFeatures] = Field(default_factory=lambda: LLMFeatures())
