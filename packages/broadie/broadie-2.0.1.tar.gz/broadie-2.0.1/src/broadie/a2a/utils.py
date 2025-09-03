from fastapi import Request

from broadie.config import settings


def extract_capabilities(agent) -> list[dict]:
    capabilities = []
    for tool in agent.agent_tools():
        capabilities.append(
            {
                "capability": getattr(tool, "name", tool.name),
                "tool_name": tool.get_name(),
                "description": getattr(tool, "description", tool.description or ""),
            },
        )
    return capabilities


def verify_auth(request: Request) -> bool:
    """Check Authorization header against configured secret."""
    if not settings.A2A_ENABLED:
        return True  # no auth needed if disabled (dev mode)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False

    # Expect: Authorization: Bearer <secret>
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        return False

    return token.strip() == settings.A2A_REGISTRY_SECRET
