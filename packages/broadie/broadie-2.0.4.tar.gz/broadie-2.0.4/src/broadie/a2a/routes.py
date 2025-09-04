from a2a.server.agent_execution.simple_request_context_builder import (
    SimpleRequestContextBuilder,
)
from a2a.server.events import EventQueue
from a2a.types import AgentCard, SendMessageRequest, SendMessageResponse
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from broadie.config import settings

from .utils import extract_capabilities, verify_auth


def add_a2a_routes(app: FastAPI, agent):
    path = f"/agent/{agent.a2a_id}"

    @app.get(f"{path}/card", response_model=AgentCard)
    async def card():
        return AgentCard(
            name=agent.name,
            description=agent.label,
            url=f"http://{settings.HOST}:{settings.PORT}{path}/sendMessage",
            capabilities=extract_capabilities(agent),
        )

    @app.get(f"{path}/capabilities")
    async def capabilities():
        return extract_capabilities(agent)

    @app.post(f"{path}/sendMessage", response_model=SendMessageResponse)
    async def send_message(req: SendMessageRequest, request: Request):
        if not verify_auth(request):
            return JSONResponse(status_code=401, content={"error": "unauthorized"})

        # 1. Build request context
        ctx_builder = SimpleRequestContextBuilder()
        context = await ctx_builder.build(
            params=req.params,
            task_id=req.params.message.taskId,
            context_id=req.params.message.contextId,
        )

        # 2. Prepare event queue
        event_queue = EventQueue()

        # 3. Execute agent logic
        await agent.execute(context, event_queue)

        # 4. Collect final task from queue
        #    (depends on your queue implementation; here’s a simple pattern)
        final_task = None
        while not event_queue.empty():
            event = await event_queue.get()
            if hasattr(event, "task"):  # Task or TaskStatusUpdateEvent
                final_task = event.task

        if final_task is None:
            return JSONResponse(status_code=500, content={"error": "no task produced"})

        # 5. Wrap into SendMessageResponse
        return SendMessageResponse.build_success(task=final_task)
