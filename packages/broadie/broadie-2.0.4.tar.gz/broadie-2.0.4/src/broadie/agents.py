from __future__ import annotations

import asyncio
import datetime
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import langsmith as ls
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from broadie.config import settings

from .channels import ChannelsAgent
from .mixins import PersistenceMixin
from .prompts import BASE_INSTRUCTIONS
from .schemas import (
    AgentSchema,
    BaseDefaultOutput,
    ChannelSchema,
    ModelSchema,
    SubAgentSchema,
)
from .tools.memory import build_memory_tools
from .tools.tasks import create_tasks, update_task
from .utils import slugify


class BaseAgent(PersistenceMixin, ABC):
    def __init__(
        self,
        name: str,
        model: ModelSchema,
        tools: list[str | Callable],
        strict_mode: bool = True,
        label: str | None = None,
        instruction: str = "You are a helpful assistant.",
        output_schema: dict[str, Any] | None = None,
        deliver_to_channels: bool = True,
    ):
        PersistenceMixin.__init__(self)
        super().__init__()
        self.label = label or name
        self.id = slugify(name)
        self.name = name
        self.model = model
        self.tools = tools
        self.instruction = instruction
        self.strict_mode = strict_mode
        self.output_schema = output_schema or BaseDefaultOutput
        self.runtime = None
        self.deliver_to_channels = deliver_to_channels
        self.channels = []
        self.channels_agent = None

    @staticmethod
    def _inbuilt_tools() -> list[Callable]:
        """Always available tools for all agents."""
        return [create_tasks, update_task]

    @property
    def recursion_limit(self) -> int:
        return settings.RECURSION_LIMIT or max(
            15,
            len(self._inbuilt_tools() + self.agent_tools()) + 10,
        )

    def initialize_runtime(self):
        model_id = f"{self.model.provider.value}:{self.model.name}"
        self.runtime = create_react_agent(
            model=model_id,
            tools=self._inbuilt_tools() + self.agent_tools(),
            prompt=self.instruction + BASE_INSTRUCTIONS,
            response_format=self.output_schema,
            store=self.store,
            checkpointer=self.checkpointer,
            debug=settings.DEBUG or False,
        )

    def get_identity(self):
        return {"id": self.id, "name": self.name, "label": self.label, "type": "agent"}

    async def _deliver_to_channels(self, raw_output, thread_id, message_id, run_id):
        if not self.channels or not self.channels_agent:
            return
        tasks = []
        for ch in self.channels:
            if not ch.enabled:
                continue
            tasks.append(
                self.channels_agent.run(
                    channel=ch,
                    output=raw_output,
                    thread_id=thread_id,
                    message_id=message_id,
                    run_id=run_id,
                ),
            )
        if tasks:
            await asyncio.gather(*tasks)

    async def run(
        self,
        message: str,
        thread_id: str | None = None,
        message_id: str | None = None,
        parent_id: str | None = "",
    ):
        thread_id = thread_id or str(uuid.uuid4())
        message_id = message_id or str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        parent_id = parent_id
        with ls.trace(
            name=f"Agent Run: {self.label}",
            run_type="chain",
            inputs={"message": message},
            tags=[f"{self.label}", parent_id],
            metadata={
                "thread_id": thread_id,
                "run_id": run_id,
                "parent_id": parent_id,
            },
        ) as rt:
            try:
                rt.metadata["started_at"] = str(
                    datetime.datetime.now(datetime.timezone.utc),
                )

                result = await self.runtime.ainvoke(
                    Command(
                        update={
                            "messages": [
                                {"role": "user", "content": message, "id": message_id},
                            ],
                        },
                    ),
                    config={
                        "configurable": {"thread_id": thread_id},
                        "run_id": run_id,
                        "recursion_limit": self.recursion_limit,
                        "metadata": {
                            "agent": self.id,
                            "label": self.label,
                            "message_id": message_id,
                        },
                    },
                )
                # --- OUTPUT HANDLING ---
                if "structured_response" in result:
                    raw_output = result["structured_response"]
                else:
                    raw_output = {
                        "result": (result["messages"][-1].content if result["messages"] else ""),
                    }
                if self.deliver_to_channels:
                    asyncio.create_task(
                        self._deliver_to_channels(
                            raw_output,
                            thread_id,
                            message_id,
                            run_id,
                        ),
                    )

                return raw_output

            except Exception as e:
                raise e

            finally:
                rt.metadata["completed_at"] = str(
                    datetime.datetime.now(datetime.timezone.utc),
                )

    @abstractmethod
    def agent_tools(self) -> list[Callable]:
        """Subclass must return list of tools to include."""
        raise NotImplementedError


class SubAgent(BaseAgent):
    def __init__(
        self,
        config: SubAgentSchema,
        parent: Agent = None,
        deliver_to_channels: bool = False,
    ):
        super().__init__(
            name=config.name,
            model=config.model or (parent.model if parent else None),
            tools=config.tools,
            strict_mode=config.strict_mode,
            label=config.description or config.name,
            instruction=config.prompt or "You are a specialized sub-agent.",
            output_schema=config.output_schema,
            deliver_to_channels=deliver_to_channels,
        )
        self.config = config
        self.parent = parent
        self.initialize_runtime()
        self.channels: list[ChannelSchema] = config.channels
        self.channels_agent = ChannelsAgent(self.model) if self.channels else None

    def agent_tools(self) -> list[Callable]:
        return self.tools


class Agent(BaseAgent):
    def __init__(self, config: AgentSchema, deliver_to_channels: bool = True):
        super().__init__(
            name=config.name,
            model=config.model,
            tools=config.tools,
            strict_mode=config.strict_mode,
            label=config.description or config.name,
            instruction=config.instruction,
            output_schema=config.output_schema,
            deliver_to_channels=deliver_to_channels,
        )
        self.config = config
        self.channels: list[ChannelSchema] = config.channels
        self.channels_agent = ChannelsAgent(self.model) if self.channels else None
        self.subagents: list[SubAgent] = [SubAgent(sa, parent=self) for sa in config.subagents]
        self.subagent_tools = self._wrap_subagents_as_tools()
        self.initialize_runtime()

    def _wrap_subagents_as_tools(self):
        wrappers = []
        for sa in self.subagents:

            @tool(
                f"delegate_to_{sa.id}",
                description=sa.instruction,
                parse_docstring=True,
            )
            async def _delegate(
                query: str,
                thread_id: str | None = None,
                message_id: str | None = None,
                _sa=sa,
            ):
                """Delegate the query to the sub-agent specialized in this task.

                Args:
                    query (str): The user query to be processed by the sub-agent.
                    thread_id (str, optional): Identifier for the conversation thread.
                    message_id (str, optional): Unique identifier for the message.

                Returns:
                    dict: The structured response from the sub-agent.

                """
                thread_id = thread_id or str(uuid.uuid4())
                message_id = message_id or str(uuid.uuid4())
                return await _sa.run(
                    query,
                    thread_id=thread_id,
                    message_id=message_id,
                    parent_id=self.id,
                )

            wrappers.append(_delegate)
        return wrappers

    def agent_tools(self) -> list[Callable]:
        return self.tools + self.subagent_tools + build_memory_tools(self)
