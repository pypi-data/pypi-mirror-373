import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from broadie import BaseAgent


def add_playground_route(app: FastAPI, agent: BaseAgent):
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    # Mount only once globally if you have assets like JS/CSS
    if not any(r.path == "/static" for r in app.router.routes):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Serve agent-specific playground
    @app.get(f"/{agent.id}/playground")
    async def serve_playground():
        return FileResponse(os.path.join(static_dir, "index.html"))
