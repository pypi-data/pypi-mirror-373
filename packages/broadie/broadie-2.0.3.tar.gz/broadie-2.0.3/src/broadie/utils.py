import logging
import re
import uuid


def slugify(value: str) -> str:
    """Convert a string into a slugified ID (lowercase, alphanumeric, dash)."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or str(uuid.uuid4())


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
