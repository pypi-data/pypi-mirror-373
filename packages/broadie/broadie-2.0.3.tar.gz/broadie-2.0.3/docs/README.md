# Broadie

**Opinionated AI Agent Framework for Reducing Hallucination**

Broadie is a production-ready framework for building AI agents with LangGraph and LangServe. It drastically reduces hallucination through structured contracts between agents, LLMs, and tools using Pydantic models.

## 🎯 Philosophy

Broadie is **opinionated by design**. We believe AI agents should:
- Use **strict Pydantic schemas** to enforce structured outputs and reduce hallucination
- Define **clear contracts** between agents, LLMs, and tools
- Leverage **built-in memory and persistence** for stateful conversations
- Support **agent-to-agent (a2a) communication** through a central registry
- Provide **easy deployment** with minimal configuration

This opinionated approach reduces hallucination by a **huge margin** compared to free-form text generation.

## 🚀 Installation

```bash
# Install broadie
pip install broadie

# For development
pip install broadie[dev]
```

## 📚 Quick Examples

### Simple Agent

```python
import asyncio
from broadie import create_agent

# Create a basic agent
simple_agent = create_agent(
    name="simple_helper",
    instruction="Be a helpful assistant, respond appropriately to user messages",
)

async def main():
    response = await simple_agent.run("Hello, can you help me with something?")
    print(response)

asyncio.run(main())
```

**Run this example:**
```bash
# Direct execution
python simple_agent.py

# Using broadie CLI
broadie chat examples/simple.py:simple_agent

# Serve as API endpoint (includes built-in playground)
broadie serve examples/simple.py:simple_agent --port 8000
```

### Agent with Tools

```python
import asyncio
from pydantic import BaseModel, Field
from broadie import create_agent, tool, ToolResponse

# Define a custom tool using ToolResponse
@tool("lookup_weather", description="Get weather information for a location")
def lookup_weather(location: str) -> ToolResponse:
    """Look up weather for a given location."""
    return ToolResponse.success(
        message=f"Weather lookup completed for {location}",
        data={"location": location, "temperature": "22°C", "condition": "sunny"},
        meta={"source": "weather_api", "lookup_type": "current"}
    )

# Define structured output using Pydantic
class WeatherOutput(BaseModel):
    summary: str = Field(..., description="Human-readable weather summary")
    location: str = Field(..., description="The location queried")
    temperature: str = Field(..., description="Current temperature")
    recommendation: str = Field(..., description="What the user should do based on weather")

# Create agent with tool and structured output
weather_agent = create_agent(
    name="weather_assistant",
    instruction="Help users with weather information and provide recommendations",
    tools=[lookup_weather],
    output_schema=WeatherOutput
)

async def main():
    response = await weather_agent.run("What's the weather like in Boston?")
    print(response)

asyncio.run(main())
```

**Run this example:**
```bash
# Direct execution
python weather_agent.py

# Using broadie CLI
broadie chat examples/weather_agent.py:weather_agent

# Serve as API endpoint (includes built-in playground)
broadie serve examples/weather_agent.py:weather_agent --port 8000
```

### Advanced Agent with ToolResponse

This example demonstrates how broadie reduces hallucination by enforcing strict contracts between agents, tools, and LLMs using Pydantic models and ToolResponse:

```python
import asyncio
from enum import Enum
from pydantic import BaseModel, Field
from broadie import create_agent, create_sub_agent, tool, ToolResponse

# Define enums for structured responses - this prevents LLM hallucination
class Verdict(str, Enum):
    malicious = "malicious"
    suspicious = "suspicious"
    benign = "benign"
    unknown = "unknown"

class EnrichmentResult(BaseModel):
    indicator: str
    type: str
    verdict: Verdict

class ThreatIntelOutput(BaseModel):
    summary: str = Field(..., description="Human-readable summary of the threat analysis")
    enrichments: list[EnrichmentResult] = Field(..., description="List of enriched indicators with verdicts")

# Tool using ToolResponse - enforces structured output contract
@tool("lookup_ip", description="Look up IP reputation in a threat intel database")
def lookup_ip(ip: str) -> ToolResponse:
    """Look up IP reputation using ToolResponse pattern."""
    reputation = "malicious" if ip.startswith("192.") else "clean"
    return ToolResponse.success(
        message=f"IP {ip} reputation lookup completed",
        data={"ip": ip, "reputation": reputation},
        meta={"source": "threat_intel_db", "lookup_type": "ip"}
    )

@tool("lookup_domain", description="Check domain reputation in DNS and threat feeds")
def lookup_domain(domain: str) -> ToolResponse:
    """Check domain reputation using ToolResponse pattern."""
    category = "phishing" if "phish" in domain else "benign"
    return ToolResponse.success(
        message=f"Domain {domain} reputation lookup completed",
        data={"domain": domain, "category": category},
        meta={"source": "dns_threat_feeds", "lookup_type": "domain"}
    )

# Create specialized subagent
indicator_enricher = create_sub_agent(
    name="indicator_enricher",
    prompt="Given an IP or domain, enrich it with threat intel context.",
    output_schema=EnrichmentResult,
    tools=[lookup_ip, lookup_domain],
)

# Main threat intelligence agent
threat_intel_agent = create_agent(
    name="threat_intel",
    instruction="You are a threat intelligence assistant. Analyze indicators and produce structured enrichment.",
    output_schema=ThreatIntelOutput,
    tools=[lookup_ip, lookup_domain],
    subagents=[indicator_enricher],
    channels=[{  # Built-in Slack integration
        "type": "slack",
        "target": "#threat-feed",
        "instructions": "Summarize in Slack blocks"
    }]
)

async def main():
    email_message = "Hello user, please reset your password here: http://bad-link.com"
    result = await threat_intel_agent.run(email_message)
    print(result)

asyncio.run(main())
```

**Run this example:**
```bash
# Direct execution
python examples/standard.py

# Using broadie CLI
broadie chat examples/standard.py:phish_guardian

# Serve as API endpoint (includes built-in playground)
broadie serve examples/standard.py:phish_guardian --port 8000
```

The **ToolResponse** pattern ensures that tools return structured data that the LLM cannot hallucinate or modify - the contract is enforced at the type level.

## 📡 Configuring Channels

To enable Slack and email notifications from your agents, you need to set the following environment variables:

### Slack Configuration

```bash
# Slack Bot Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
```

**How to get Slack credentials:**
- **Bot Token**: Create a Slack app at [api.slack.com/apps](https://api.slack.com/apps), go to "OAuth & Permissions" and install the app to get your bot token
- **Signing Secret**: Found in your Slack app settings under "Basic Information" → "App Credentials"

### Email/SMTP Configuration

```bash
# SMTP Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
EMAIL_FROM=alerts@yourdomain.com
```

**How to get SendGrid credentials:**
- Sign up at [sendgrid.com](https://sendgrid.com)
- Create an API key in Settings → API Keys
- Use `apikey` as the username and your API key as the password
- Verify your sender email address in SendGrid

Once configured, your agents will automatically send notifications to the specified channels when they complete their tasks.

## 📊 Tracing and Observability

broadie integrates with **LangSmith** (by LangChain) for comprehensive tracing and observability of your agents. This allows you to monitor agent performance, debug issues, and view detailed execution traces.

### LangSmith Configuration

```bash
# LangSmith Tracing Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=broadie
```

**Environment Variables:**
- **LANGCHAIN_TRACING_V2**: Set to `true` to enable LangSmith tracing (default: `false`)
- **LANGCHAIN_ENDPOINT**: LangSmith API endpoint (default: `https://api.smith.langchain.com`)
- **LANGCHAIN_API_KEY**: Your LangSmith API key for authentication (required for tracing)
- **LANGCHAIN_PROJECT**: Project name to organize your traces (default: `broadie`)

**How to get LangSmith credentials:**
1. Sign up at [smith.langchain.com](https://smith.langchain.com) (FREE tier available)
2. Create a new project or use an existing one
3. Go to Settings → API Keys and create a new API key
4. Set the environment variables above with your credentials

**Viewing traces and tools:**
- Visit [smith.langchain.com](https://smith.langchain.com) and navigate to your project
- View detailed traces showing agent execution, tool calls, and LLM interactions
- Monitor performance metrics, token usage, and execution times
- Debug issues by examining failed runs and error traces
- Analyze tool usage patterns and optimize agent performance

Once configured, all agent runs will be automatically traced and visible in the LangSmith dashboard.

## 🏗️ Core Architecture

### The Contract System

broadie enforces **contracts** between three key components:

1. **Agent Contract**: Defines what the agent can do, its tools, and expected outputs
2. **LLM Contract**: Structured via Pydantic schemas to prevent hallucination  
3. **Tool Contract**: Type-safe tool definitions with clear input/output schemas

```python
# This contract prevents the LLM from hallucinating invalid data structures

from pydantic import BaseModel, Field
from broadie import create_agent
from typing import List


class UserProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150) 
    email: str = Field(..., description="it contains an @ symbol")
    preferences: List[str] = Field(default_factory=list)

agent = create_agent(
    name="user_manager",
    output_schema=UserProfile,  # Enforces structure
    instruction="Extract user information from text"
)
```

### Built-in Memory & Persistence (WIP)

Every agent has **persistent memory** by design:

```python
from broadie import create_agent
# Memory is automatic - no configuration needed
agent = create_agent(name="assistant", instruction="Remember our conversations")

# Conversations are automatically persisted across runs
response1 = await agent.run("My name is Alice", thread_id="user_123")
response2 = await agent.run("What's my name?", thread_id="user_123")  # Remembers Alice
```

### Agent-to-Agent (A2A) Communication (WIP)

broadie includes a **central registry** for agent discovery and communication:

```python
# Register your agent
await agent.register_to_registry()

# Discover other agents  
available_agents = await discover_agents(capabilities=["data_analysis"])

# Communicate with other agents
result = await agent.delegate_to("data_analyst", "Analyze this dataset")
```

## 🛠️ CLI Tools

### Chat with Your Agent

```bash
# Interactive chat session
broadie chat examples/standard.py:phish_guardian

# Chat with specific configuration
broadie chat examples/standard.py:phish_guardian --thread user123
```

### Serve Your Agent

```bash
# Expose agent via HTTP API (includes built-in playground)
broadie serve examples/standard.py:phish_guardian --port 8000

# Serve with registry registration
broadie serve examples/standard.py:phish_guardian --register --host 0.0.0.0

# Disable playground in production
PLAYGROUND_ENABLED=false broadie serve examples/standard.py:phish_guardian --port 8000
```

### Playground

The **playground** is built into the serve command and provides a web interface to test your agents:

```bash
# Serve with playground enabled (default)
broadie serve examples/standard.py:phish_guardian --port 8000

# Disable playground for production (recommended)
PLAYGROUND_ENABLED=false broadie serve examples/standard.py:phish_guardian --port 8000
```

**Note:** Always disable the playground in production environments by setting `PLAYGROUND_ENABLED=false`.

## 🚀 Easy Deployment (WIP)

Deploy your agents with minimal configuration:

```bash
# Initialize project structure
broadie init my_project

# Deploy to production
broadie deploy --config production.yaml

# Scale horizontally  
broadie scale --replicas 3
```

## 🔧 Upcoming Features

- **Multi-model Support**: Google VertexAI, OpenAI, Anthropic, and custom providers
- **Monitoring**: Prometheus metrics, structured logging, health checks
- **Security**: Enterprise authentication, authorization, audit logging

## 📞 Support

For questions, issues, or contributions:

**Email**: scientific-computing@broadinstitute.org

## 🤝 Contributing

broadie is developed by the Broad Institute. We welcome contributions! See our contributing guidelines for details.

---

**Built with ❤️ by the Broad Institute**