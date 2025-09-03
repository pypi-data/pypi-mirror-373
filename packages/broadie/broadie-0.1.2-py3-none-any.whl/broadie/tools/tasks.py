import json
import os
import tempfile
import time
import uuid

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from broadie.config import settings
from broadie.tools.channels import ToolResponse


# Input schemas for task tools
class CreateTasksInput(BaseModel):
    thread_id: str = Field(description="Thread identifier for task list")
    tasks: list[str] = Field(description="List of task descriptions to create")
    agent: str = Field(
        default="unknown",
        description="Agent identifier creating the tasks",
    )
    tool: str = Field(
        default="create_tasks",
        description="Tool name creating the tasks",
    )


class UpdateTaskInput(BaseModel):
    thread_id: str = Field(description="Thread identifier for task list")
    task_id: str = Field(description="Unique identifier of the task to update")
    done: bool = Field(description="Whether the task is completed or not")
    agent: str = Field(
        default="unknown",
        description="Agent identifier updating the task",
    )
    tool_used: str = Field(
        default="update_task",
        description="Tool name used for the update",
    )


_TASKS: dict[str, list[dict]] = {}
_TEMP_DIR = settings.TASK_TEMP_DIR or os.path.join(tempfile.gettempdir(), "agent_tasks")
os.makedirs(_TEMP_DIR, exist_ok=True)
_TTL_SECONDS = settings.TASK_TTL_SECONDS


def _thread_file(thread_id: str) -> str:
    return os.path.join(_TEMP_DIR, f"{thread_id}.json")


def _ensure_thread(thread_id: str):
    """Ensure a task list exists for a thread (load from file if fresh enough)."""
    if thread_id not in _TASKS:
        path = _thread_file(thread_id)
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            if time.time() - data["ts"] < _TTL_SECONDS:
                _TASKS[thread_id] = data["tasks"]
            else:
                os.remove(path)
                _TASKS[thread_id] = []
        else:
            _TASKS[thread_id] = []


def _persist(thread_id: str):
    """Persist tasks for thread to a temp file with a timestamp."""
    path = _thread_file(thread_id)
    payload = {"ts": time.time(), "tasks": _TASKS[thread_id]}
    with open(path, "w") as f:
        json.dump(payload, f)


@tool(
    "create_tasks",
    args_schema=CreateTasksInput,
    description="Create or overwrite the task list for this thread.",
)
def create_tasks(
    thread_id: str,
    tasks: list[str],
    agent: str = "unknown",
    tool: str = "create_tasks",
) -> ToolResponse:
    start_time = time.time()
    try:
        _ensure_thread(thread_id)

        # Limit tasks to configured maximum
        limited_tasks = tasks[: settings.TASK_LIMIT_PER_THREAD]
        if len(tasks) > settings.TASK_LIMIT_PER_THREAD:
            truncated_count = len(tasks) - settings.TASK_LIMIT_PER_THREAD
        else:
            truncated_count = 0

        _TASKS[thread_id] = [
            {
                "id": str(uuid.uuid4()),
                "title": t,
                "done": False,
                "agent": agent,
                "tool": tool,
                "created_at": time.time(),
            }
            for t in limited_tasks
        ]
        _persist(thread_id)

        return ToolResponse.success(
            message=f"Successfully created {len(_TASKS[thread_id])} tasks for thread {thread_id}",
            data={
                "thread_id": thread_id,
                "tasks": _TASKS[thread_id],
                "created_count": len(_TASKS[thread_id]),
                "truncated_count": truncated_count,
            },
            meta={
                "thread_id": thread_id,
                "agent": agent,
                "tool": tool,
                "task_limit": settings.TASK_LIMIT_PER_THREAD,
                "original_count": len(tasks),
                "final_count": len(_TASKS[thread_id]),
            },
            tool_name="create_tasks",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    except Exception as e:
        return ToolResponse.fail(
            message=f"Failed to create tasks for thread {thread_id}",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "thread_id": thread_id,
                "task_count": len(tasks),
            },
            meta={"thread_id": thread_id, "agent": agent},
            tool_name="create_tasks",
            execution_time_ms=(time.time() - start_time) * 1000,
        )


@tool(
    "update_task",
    args_schema=UpdateTaskInput,
    description="Update the status (done/not done) of an existing task.",
)
def update_task(
    thread_id: str,
    task_id: str,
    done: bool,
    agent: str = "unknown",
    tool_used: str = "update_task",
) -> ToolResponse:
    start_time = time.time()
    try:
        _ensure_thread(thread_id)

        # Find and update the task
        for t in _TASKS[thread_id]:
            if t["id"] == task_id:
                old_status = t["done"]
                t["done"] = done
                t["agent"] = agent
                t["tool"] = tool_used
                t["updated_at"] = time.time()
                _persist(thread_id)

                status_change = (
                    "completed" if done and not old_status else "reopened" if not done and old_status else "updated"
                )

                return ToolResponse.success(
                    message=f"Successfully {status_change} task '{t['title']}' in thread {thread_id}",
                    data={
                        "task": t,
                        "thread_id": thread_id,
                        "task_id": task_id,
                        "status_change": status_change,
                        "old_status": old_status,
                        "new_status": done,
                    },
                    meta={
                        "thread_id": thread_id,
                        "task_id": task_id,
                        "agent": agent,
                        "tool_used": tool_used,
                        "status_change": status_change,
                    },
                    tool_name="update_task",
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

        # Task not found
        return ToolResponse.fail(
            message=f"Task with ID {task_id} not found in thread {thread_id}",
            error_details={
                "error_type": "TaskNotFound",
                "task_id": task_id,
                "thread_id": thread_id,
                "available_task_count": len(_TASKS[thread_id]),
            },
            meta={
                "thread_id": thread_id,
                "task_id": task_id,
                "available_tasks": [t["id"] for t in _TASKS[thread_id]],
            },
            tool_name="update_task",
            execution_time_ms=(time.time() - start_time) * 1000,
        )

    except Exception as e:
        return ToolResponse.fail(
            message=f"Failed to update task {task_id} in thread {thread_id}",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "thread_id": thread_id,
                "task_id": task_id,
            },
            meta={"thread_id": thread_id, "task_id": task_id, "agent": agent},
            tool_name="update_task",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
