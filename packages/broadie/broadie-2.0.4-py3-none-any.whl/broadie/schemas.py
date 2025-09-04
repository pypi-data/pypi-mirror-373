from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    pass


class BaseDefaultOutput(BaseModel):
    """Fallback schema for any Agent or SubAgent without a custom schema."""

    result: str = Field(
        description="Default string result when no structured schema is provided",
    )
    success: bool | None = Field(
        default=True,
        description="Indicates if the operation was successful",
    )
    error: str | None = Field(
        default=None,
        description="Error message if validation or execution failed",
    )


class ModelProvider(str, Enum):
    google = "google_vertexai"
    openai = "openai"
    anthropic = "anthropic"
    ollama = "ollama"  # example: local inference
    custom = "custom"  # allow extension


class ModelSchema(BaseSchema):
    """Configuration for model provider + settings."""

    provider: ModelProvider = ModelProvider.google
    name: str = "gemini-2.0-flash"
    settings: dict[str, Any] = {}  # any provider-specific overrides


class ChannelType(str, Enum):
    slack = "slack"
    api = "api"
    email = "email"


class ChannelSchema(BaseSchema):
    """Represents an output channel for delivering agent results."""

    type: ChannelType
    target: str | None = None
    instructions: str | None = None
    enabled: bool = True


class SubAgentSchema(BaseSchema):
    name: str
    description: str | None = None
    prompt: str | None = None
    tools: list[str | Callable] = []
    model: ModelSchema | None = None
    output_schema: type[BaseModel] | None = BaseDefaultOutput
    strict_mode: bool = True
    channels: list[ChannelSchema] = []


class AgentSchema(BaseSchema):
    name: str
    description: str | None = None
    instruction: str
    model: ModelSchema = ModelSchema()
    tools: list[str | Callable] = []
    temperature: float = 0.2
    max_tokens: int = 50000
    max_retries: int = 2
    subagents: list[SubAgentSchema] = []
    output_schema: type[BaseModel] | None = BaseDefaultOutput
    strict_mode: bool = True
    channels: list[ChannelSchema] = []
