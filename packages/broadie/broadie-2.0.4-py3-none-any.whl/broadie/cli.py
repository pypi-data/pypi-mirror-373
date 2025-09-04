# broadie/cli.py
import asyncio
import importlib
import importlib.util
import pathlib
import secrets
import sys
import uuid
import warnings
from contextlib import asynccontextmanager

import click
import uvicorn
from fastapi import FastAPI

from broadie.a2a.register import register_agent_with_registry
from broadie.a2a.routes import add_a2a_routes
from broadie.config import settings
from broadie.server import add_agent_routes, create_app
from broadie.server.playground import add_playground_route

warnings.filterwarnings(
    "ignore",
    message="This feature is deprecated as of June 24, 2025",
    module="vertexai._model_garden._model_garden_models",
)

warnings.filterwarnings(
    "ignore",
    message=r"Key 'additionalProperties' is not supported in schema, ignoring",
)


# ----------------------------
# Helpers
# ----------------------------
def ensure_env_file():
    """Check if .env file exists, create one with API_KEY if not."""
    env_path = pathlib.Path(".env")
    if not env_path.exists():
        api_key = secrets.token_urlsafe(48)

        # Create .env file with API_KEY
        with open(env_path, "w") as f:
            f.write(f"API_KEY={api_key}\n")

        click.secho(
            "✅ Created .env file with API_KEY, you will use this when APIKeyHeader (apiKey) is needed "
            "example to call /invoke",
            fg="green",
        )
    else:
        click.secho(
            "🔍 Found existing .env file, you will use this when APIKeyHeader (apiKey) is needed "
            "example to call /invoke",
            fg="blue",
        )


def load_agent_from_path(path: str):
    """Load an agent from 'file.py:agent_name' or 'module:agent_name'."""
    try:
        module_path, agent_name = path.split(":")
    except ValueError:
        raise click.ClickException("❌ Invalid format. Use file.py:agent_name")

    p = pathlib.Path(module_path)
    if p.exists() and p.suffix == ".py":  # local .py file
        spec = importlib.util.spec_from_file_location(p.stem, str(p))
        module = importlib.util.module_from_spec(spec)
        sys.modules[p.stem] = module
        spec.loader.exec_module(module)  # type: ignore
    else:  # treat as dotted import
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            raise click.ClickException(f"❌ Could not import '{module_path}'")

    if not hasattr(module, agent_name):
        raise click.ClickException(f"❌ '{agent_name}' not found in '{module_path}'")

    return getattr(module, agent_name)


async def prepare_agent(agent):
    if hasattr(agent, "init_checkpointer"):
        await agent.init_checkpointer()
    if hasattr(agent, "init_store"):
        await agent.init_store()
    return agent


# ----------------------------
# CLI
# ----------------------------
@click.group()
def main():
    """🔒 Broadie — Build and serve AI Agents with ease."""
    click.secho("🚀 Broadie CLI started", fg="green", bold=True)
    ensure_env_file()


@main.command("version")
def version():
    """Show version information."""
    from broadie import __version__

    click.echo(f"Broadie AI Framework v{__version__}")


@main.command("serve")
@click.argument("target", type=str)
@click.option("--host", default=settings.HOST, type=str)
@click.option("--port", default=settings.PORT, type=int)
@click.option("--workers", default=1, type=int, help="Number of worker processes")
def serve(target, host, port, workers):
    """Serve a single agent.

    TARGET must be:
    - file.py:agent_name
    - dotted.module:agent_name
    """
    agent = load_agent_from_path(target)
    agent.a2a_id = str(uuid.uuid4())
    agent = asyncio.run(prepare_agent(agent))  # async-safe init
    asyncio.run(register_agent_with_registry(agent))

    @asynccontextmanager
    async def lifespan(fapp: FastAPI):
        click.secho(f"🔄 Initializing agent '{agent.id}'", fg="cyan")
        yield
        if hasattr(agent, "close"):
            agent.close()
            click.secho(
                f"🧹 Cleaned up persistence for agent '{agent.id}'",
                fg="yellow",
            )

    app: FastAPI = create_app(lifespan=lifespan)
    add_agent_routes(app, agent)
    add_a2a_routes(app, agent)
    if settings.PLAYGROUND_ENABLED:
        add_playground_route(app, agent)

    click.secho(
        f"✅ Serving agent '{agent.id}' at http://{host}:{port}/{agent.id}/playground",
        fg="green",
        bold=True,
    )

    uvicorn.run(app, host=host, port=port, workers=workers)


@main.command("chat")
@click.argument("target", type=str)
def chat(target):
    """Run an agent in CLI chat mode.

    TARGET must be:
    - file.py:agent_name
    - dotted.module:agent_name
    """

    async def start():
        agent = load_agent_from_path(target)
        agent = await prepare_agent(agent)
        click.secho(f"💬 Chatting with agent '{agent.id}' (Ctrl+C to quit)", fg="cyan")

        while True:
            try:
                user_msg = click.prompt("You")
                resp = await agent.run(user_msg)
                click.secho(f"{agent.id}> {resp}", fg="green")
            except KeyboardInterrupt:
                click.secho("\n👋 Exiting chat", fg="red")
                break

    asyncio.run(start())
