# broadie/builders.py
from typing import Any

from pydantic import BaseModel

from .agents import Agent
from .schemas import (
    AgentSchema,
    BaseDefaultOutput,
    ChannelSchema,
    ModelProvider,
    ModelSchema,
    SubAgentSchema,
)


def _build_channels(
    channels: list[ChannelSchema | dict[str, Any]] | None,
) -> list[ChannelSchema]:
    if not channels:
        return []
    built = []
    for ch in channels:
        if isinstance(ch, ChannelSchema):
            built.append(ch)
        elif isinstance(ch, dict):
            built.append(ChannelSchema(**ch))
        else:
            raise ValueError(f"Invalid channel type: {type(ch)}")
    return built


def create_sub_agent(
    name: str,
    prompt: str,
    tools: list[Any] | None = None,
    description: str | None = None,
    model: ModelSchema | None = None,
    output_schema: type[BaseModel] | None = None,
    strict_mode: bool = True,
) -> SubAgentSchema:
    return SubAgentSchema(
        name=name,
        description=description or name,
        prompt=prompt,
        tools=tools or [],
        model=model,
        output_schema=(output_schema.model_rebuild() if output_schema else BaseDefaultOutput.model_rebuild()),
        strict_mode=strict_mode,
    )


def create_agent(
    name: str,
    instruction: str,
    model: str | ModelSchema = "gemini-2.0-flash",
    provider: str | ModelProvider = ModelProvider.google,
    tools: list[Any] | None = None,
    description: str | None = None,
    channels: list[ChannelSchema | dict[str, Any]] | None = None,
    subagents: list[SubAgentSchema | dict[str, Any]] | None = None,
    output_schema: type[BaseModel] | None = None,
    strict_mode: bool = True,
) -> Agent:
    if isinstance(model, str):
        model = ModelSchema(provider=provider, name=model)
    if isinstance(provider, str):
        provider = ModelProvider(provider)

    built_channels = _build_channels(channels)
    built_subagents = []
    if subagents:
        for sa in subagents:
            if isinstance(sa, SubAgentSchema):
                built_subagents.append(sa)
            elif isinstance(sa, dict):
                built_subagents.append(SubAgentSchema(**sa))
            else:
                raise ValueError(f"Invalid subagent type: {type(sa)}")

    schema = AgentSchema(
        name=name,
        description=description or instruction,
        instruction=instruction,
        model=model,
        tools=tools or [],
        channels=built_channels,
        subagents=built_subagents,
        output_schema=output_schema or BaseDefaultOutput,
        strict_mode=strict_mode,
    )
    return Agent(schema)
