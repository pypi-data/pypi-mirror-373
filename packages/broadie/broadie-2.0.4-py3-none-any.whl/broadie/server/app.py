import time
import uuid

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from broadie.config import settings
from broadie.server.credentials import check_credentials


def create_app(**kwargs) -> FastAPI:
    app = FastAPI(**kwargs)

    # Use values from BROADIE_ config
    allow_origins = settings.CORS_ORIGINS or ["*"] if settings.DEBUG else settings.CORS_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    return app


class ChatRequest(BaseModel):
    message: str
    thread_id: str = uuid.uuid4()


def add_agent_routes(app: FastAPI, agent):
    path = f"/agent/{agent.id}"

    @app.get("/")
    async def root():
        return {"message": "Welcome to the AI Agent API"}

    @app.get(f"{path}/info", dependencies=[Depends(check_credentials)])
    async def info():
        return agent.get_identity()

    @app.post(f"{path}/invoke", dependencies=[Depends(check_credentials)])
    async def invoke(req: ChatRequest):
        resp = await agent.run(req.message, thread_id=req.thread_id)
        return {"agent": agent.id, "response": resp}

    @app.get(f"{path}/health")
    async def health():
        return {"status": "ok", "agent": agent.id}


def add_middlewares(app: FastAPI):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration = round(time.time() - start_time, 3)
            print(f"❌ {request.method} {request.url} failed after {duration}s: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "error": str(exc)},
            )
        duration = round(time.time() - start_time, 3)
        print(f"✅ {request.method} {request.url} completed in {duration}s")
        return response

    @app.middleware("http")
    async def restrict_hosts(request: Request, call_next):
        allow_hosts = settings.ALLOWED_HOSTS or ["localhost", "0.0.0.0"]
        host = request.headers.get("host", "").split(":")[0]
        if host not in allow_hosts and not settings.DEBUG:
            return JSONResponse(status_code=403, content={"detail": "Host not allowed"})
        return await call_next(request)
