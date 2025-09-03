# src/broadie/tools/memory.py
import datetime
import time
import uuid
from typing import Any

from langchain_core.tools import tool
from langgraph.config import get_config
from pydantic import BaseModel, Field

from broadie.tools.channels import ToolResponse


# Input schemas for memory tools
class RememberFactInput(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")
    fact: dict[str, Any] = Field(description="Fact data to remember about the user")


class RecallFactsInput(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")
    query: str = Field(description="Search query to find relevant facts")
    limit: int = Field(default=3, description="Maximum number of facts to retrieve")


class ClearFactsInput(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")


class SaveMessageInput(BaseModel):
    message: dict[str, Any] = Field(
        description="Message data to save to conversation history",
    )


class GetHistoryInput(BaseModel):
    limit: int = Field(
        default=20,
        description="Maximum number of history items to retrieve",
    )


def build_memory_tools(agent):
    """Build memory tools bound to a specific agent instance (PersistenceMixin).
    Thread_id is auto-injected from config; user_id can be passed explicitly.
    """

    # ------------------------
    # Long-term facts (user profile)
    # ------------------------
    @tool(
        "remember_fact",
        args_schema=RememberFactInput,
        description="Save a fact about the user for long-term use",
    )
    async def remember_fact(user_id: str, fact: dict) -> ToolResponse:
        start_time = time.time()
        try:
            fact_id = await agent.remember_user_fact(user_id, fact)
            return ToolResponse.success(
                message=f"Successfully remembered fact for user {user_id}",
                data={"fact_id": fact_id, "user_id": user_id, "fact": fact},
                meta={
                    "user_id": user_id,
                    "fact_keys": list(fact.keys()) if isinstance(fact, dict) else [],
                },
                tool_name="remember_fact",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return ToolResponse.fail(
                message=f"Failed to remember fact for user {user_id}",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "user_id": user_id,
                },
                meta={"user_id": user_id},
                tool_name="remember_fact",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    @tool(
        "recall_facts",
        args_schema=RecallFactsInput,
        description="Search and retrieve facts about the user",
    )
    async def recall_facts(user_id: str, query: str, limit: int = 3) -> ToolResponse:
        start_time = time.time()
        try:
            facts = await agent.recall_user_facts(user_id, query, limit)
            return ToolResponse.success(
                message=f"Successfully retrieved {len(facts)} facts for user {user_id}",
                data={
                    "facts": facts,
                    "user_id": user_id,
                    "query": query,
                    "count": len(facts),
                },
                meta={
                    "user_id": user_id,
                    "query": query,
                    "requested_limit": limit,
                    "actual_count": len(facts),
                },
                tool_name="recall_facts",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return ToolResponse.fail(
                message=f"Failed to recall facts for user {user_id}",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "user_id": user_id,
                    "query": query,
                },
                meta={"user_id": user_id, "query": query},
                tool_name="recall_facts",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    @tool(
        "clear_facts",
        args_schema=ClearFactsInput,
        description="Clear all remembered facts for a user",
    )
    async def clear_facts(user_id: str) -> ToolResponse:
        start_time = time.time()
        try:
            result = await agent.clear_user_facts(user_id)
            cleared_count = result.get("deleted", 0) if isinstance(result, dict) else 0
            return ToolResponse.success(
                message=f"Successfully cleared {cleared_count} facts for user {user_id}",
                data={
                    "user_id": user_id,
                    "cleared_count": cleared_count,
                    "result": result,
                },
                meta={"user_id": user_id, "cleared_count": cleared_count},
                tool_name="clear_facts",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return ToolResponse.fail(
                message=f"Failed to clear facts for user {user_id}",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "user_id": user_id,
                },
                meta={"user_id": user_id},
                tool_name="clear_facts",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    # ------------------------
    # Thread memory (ephemeral with decay)
    # ------------------------
    @tool(
        "save_message",
        args_schema=SaveMessageInput,
        description="Save the current message to conversation history (auto thread_id)",
    )
    async def save_message(message: dict) -> ToolResponse:
        start_time = time.time()
        try:
            cfg = get_config()["configurable"]
            thread_id = cfg.get("thread_id", "default-thread")
            mid = str(uuid.uuid4())
            value = {**message, "_created_at": datetime.datetime.utcnow().isoformat()}
            await agent.store.aput(("threads", thread_id, "history"), mid, value)
            return ToolResponse.success(
                message=f"Successfully saved message to thread {thread_id}",
                data={"message_id": mid, "thread_id": thread_id, "saved": True},
                meta={
                    "thread_id": thread_id,
                    "message_id": mid,
                    "message_keys": (list(message.keys()) if isinstance(message, dict) else []),
                },
                tool_name="save_message",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return ToolResponse.fail(
                message="Failed to save message to conversation history",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "thread_id": (cfg.get("thread_id", "default-thread") if "cfg" in locals() else "unknown"),
                },
                meta={
                    "thread_id": (cfg.get("thread_id", "default-thread") if "cfg" in locals() else "unknown"),
                },
                tool_name="save_message",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    @tool(
        "get_history",
        args_schema=GetHistoryInput,
        description="Get recent conversation history (auto thread_id)",
    )
    async def get_history(limit: int = 20) -> ToolResponse:
        start_time = time.time()
        try:
            cfg = get_config()["configurable"]
            thread_id = cfg.get("thread_id", "default-thread")
            history = await agent.store.alist(
                ("threads", thread_id, "history"),
                limit=limit,
            )
            return ToolResponse.success(
                message=f"Successfully retrieved {len(history)} history items from thread {thread_id}",
                data={
                    "history": history,
                    "thread_id": thread_id,
                    "count": len(history),
                },
                meta={
                    "thread_id": thread_id,
                    "requested_limit": limit,
                    "actual_count": len(history),
                },
                tool_name="get_history",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return ToolResponse.fail(
                message="Failed to retrieve conversation history",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "thread_id": (cfg.get("thread_id", "default-thread") if "cfg" in locals() else "unknown"),
                    "requested_limit": limit,
                },
                meta={
                    "thread_id": (cfg.get("thread_id", "default-thread") if "cfg" in locals() else "unknown"),
                },
                tool_name="get_history",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    @tool("clear_history", description="Clear conversation history (auto thread_id)")
    async def clear_history() -> ToolResponse:
        start_time = time.time()
        try:
            cfg = get_config()["configurable"]
            thread_id = cfg.get("thread_id", "default-thread")
            result = await agent.clear_thread_history(thread_id)
            cleared_count = result.get("deleted", 0) if isinstance(result, dict) else 0
            return ToolResponse.success(
                message=f"Successfully cleared {cleared_count} history items from thread {thread_id}",
                data={
                    "thread_id": thread_id,
                    "cleared_count": cleared_count,
                    "result": result,
                },
                meta={"thread_id": thread_id, "cleared_count": cleared_count},
                tool_name="clear_history",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return ToolResponse.fail(
                message="Failed to clear conversation history",
                error_details={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "thread_id": (cfg.get("thread_id", "default-thread") if "cfg" in locals() else "unknown"),
                },
                meta={
                    "thread_id": (cfg.get("thread_id", "default-thread") if "cfg" in locals() else "unknown"),
                },
                tool_name="clear_history",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    return [
        remember_fact,
        recall_facts,
        clear_facts,
        save_message,
        get_history,
        clear_history,
    ]
