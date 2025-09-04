import httpx

from broadie.config import settings

from .utils import extract_capabilities


async def register_agent_with_registry(agent):
    if not settings.A2A_ENABLED or not settings.A2A_REGISTRY_URL:
        return

    card = {
        "id": agent.id,
        "name": agent.name,
        "description": agent.label,
        "model": agent.model.name,
        "endpoint": f"https://{settings.HOST}/agent/{agent.id}/sendMessage",
        "capabilities": extract_capabilities(agent),
        "status": "online",
        "a2a_id": agent.a2a_id,
    }

    try:
        headers = {"Authorization": f"Bearer {settings.A2A_REGISTRY_SECRET}"}
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.A2A_REGISTRY_URL}/agents/register",
                json=card,
                headers=headers,
            )
            resp.raise_for_status()

    except httpx.HTTPError as e:
        print("Failed to register agent with A2A registry:", e)
        # Log the error or handle it as needed
    except httpx.ConnectError as e:
        print("Failed to connect to A2A registry:", e)
        # Log the error or handle it as needed
