"""Broadie: Production-grade AI Agent Framework

A robust, scalable framework for building and deploying AI agents
in production environments with enterprise-grade reliability.
"""

__version__ = "0.1.0"
__author__ = "Broad Institute"
__email__ = "broadie@broadinstitute.org"
__license__ = "MIT"

from langchain_core.tools import tool

# Server subpackage
# Tools subpackage
from . import server, tools

# Core agent classes
from .agents import Agent, BaseAgent, SubAgent

# Configuration and schemas
from .config import settings

# Factory functions
from .factory import create_agent, create_sub_agent
from .schemas import AgentSchema, ChannelSchema, ModelSchema, SubAgentSchema
from .tools import ToolResponse, ToolStatus

# Utilities
from .utils import slugify

__all__ = [
    # Core classes
    "Agent",
    "BaseAgent",
    "SubAgent",
    "ToolStatus",
    "ToolResponse",
    # Factory functions
    "create_agent",
    "create_sub_agent",
    # Schemas
    "AgentSchema",
    "SubAgentSchema",
    "ModelSchema",
    "ChannelSchema",
    # Configuration
    "settings",
    # Subpackages
    "tools",
    "server",
    # Utilities
    "slugify",
    "tool",  # Re-export from langchain
    # Metadata
    "__version__",
]
