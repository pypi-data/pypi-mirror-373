# -----------------------------
# Shared response schema
# -----------------------------
from datetime import datetime
from email.message import EmailMessage
from enum import Enum
from typing import Any

import aiosmtplib
import httpx
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from broadie.config import settings


class ToolState(str, Enum):
    WORKING = "working"
    COMPLETED = "completed"  # 👈 final stop condition
    ERROR = "error"


class ToolStatus(str, Enum):
    """Standard status values for tool responses."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"
    FAILED = "failed"
    SENT = "sent"
    QUEUED = "queued"
    POSTED = "posted"
    NOT_CONFIGURED = "not_configured"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"


class ToolResponse(BaseModel):
    """Elaborate response schema for all tool operations.

    This class provides a standardized way to return responses from tools,
    with comprehensive metadata, error handling, and status tracking.
    """

    status: ToolStatus = Field(description="Status of the tool operation")
    message: str | None = Field(
        default=None,
        description="Human-readable message describing the result",
    )
    data: Any | None = Field(default=None, description="Tool-specific response data")
    error: dict | None = Field(
        default=None,
        description="Error details if status indicates failure",
    )
    meta: dict | None = Field(
        default_factory=dict,
        description="Additional metadata about the operation",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the response was created",
    )
    tool_name: str | None = Field(
        default=None,
        description="Name of the tool that generated this response",
    )
    execution_time_ms: float | None = Field(
        default=None,
        description="Time taken to execute the tool in milliseconds",
    )
    state: ToolState = ToolState.COMPLETED

    @classmethod
    def success(
        cls,
        message: str = None,
        data: Any = None,
        meta: dict = None,
        tool_name: str = None,
        execution_time_ms: float = None,
    ) -> "ToolResponse":
        """Create a successful tool response."""
        return cls(
            status=ToolStatus.SUCCESS,
            message=message,
            data=data,
            meta=meta or {},
            tool_name=tool_name,
            execution_time_ms=execution_time_ms,
            state=ToolState.COMPLETED,
        )

    @classmethod
    def fail(  # noda
        cls,
        message: str,
        error_details: dict = None,
        meta: dict = None,
        tool_name: str = None,
        execution_time_ms: float = None,
    ) -> "ToolResponse":
        """Create an error tool response."""
        return cls(
            status=ToolStatus.ERROR,
            message=message,
            error=error_details,
            meta=meta or {},
            tool_name=tool_name,
            execution_time_ms=execution_time_ms,
            state=ToolState.COMPLETED,
        )

    @classmethod
    def warning(
        cls,
        message: str,
        data: Any = None,
        meta: dict = None,
        tool_name: str = None,
        execution_time_ms: float = None,
    ) -> "ToolResponse":
        """Create a warning tool response."""
        return cls(
            status=ToolStatus.WARNING,
            message=message,
            data=data,
            meta=meta or {},
            tool_name=tool_name,
            execution_time_ms=execution_time_ms,
            state=ToolState.COMPLETED,
        )

    def model_dump_json(self, **kwargs) -> str:
        """Override to handle datetime serialization."""
        return super().model_dump_json(default=str, **kwargs)

    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return self.status in [
            ToolStatus.SUCCESS,
            ToolStatus.SENT,
            ToolStatus.POSTED,
            ToolStatus.QUEUED,
        ]

    def is_error(self) -> bool:
        """Check if the response indicates an error."""
        return self.status in [
            ToolStatus.ERROR,
            ToolStatus.FAILED,
            ToolStatus.TIMEOUT,
            ToolStatus.UNAUTHORIZED,
            ToolStatus.NOT_FOUND,
        ]

    def has_data(self) -> bool:
        """Check if the response contains data."""
        return self.data is not None


# -----------------------------
# Slack Tool
# -----------------------------
class SlackToolInput(BaseModel):
    channel: str = Field(description="Slack channel ID or name (e.g. '#general')")
    blocks: list | None = Field(
        default=None,
        description="Optional Slack block kit payloads",
    )
    text: str | None = Field(
        default="New Slack message",
        description="Fallback plain text message (used for notifications)",
    )


@tool(
    "send_slack_tool",
    args_schema=SlackToolInput,
    description="Send formatted message to Slack, using blocks when possible",
)
async def send_slack_tool(
    channel: str,
    blocks: list | None = None,
    text: str | None = None,
) -> ToolResponse:
    import time

    start_time = time.time()

    slack_token = settings.SLACK_BOT_TOKEN
    if not slack_token:
        return ToolResponse(
            status=ToolStatus.NOT_CONFIGURED,
            message="ignore not configured",
            error={"reason": "missing_token", "detail": "No Slack bot token provided"},
            meta={"channel": channel},
            tool_name="send_slack_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )

    client = AsyncWebClient(token=slack_token)
    try:
        resp = await client.chat_postMessage(
            channel=channel,
            text=text or "New Slack message",
            blocks=blocks if blocks else None,
        )
        return ToolResponse.success(
            message=f"delivered to channel {channel}",
            data={"message_ts": resp["ts"], "channel": channel},
            meta={
                "channel": channel,
                "ts": resp["ts"],
                "blocks_used": blocks is not None,
            },
            tool_name="send_slack_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    except SlackApiError as e:
        return ToolResponse.fail(
            message=f"Failed to send Slack message to {channel}",
            error_details={
                "slack_error": str(e),
                "error_code": getattr(e.response, "status_code", None),
                "channel": channel,
            },
            meta={"channel": channel},
            tool_name="send_slack_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )


# -----------------------------
# Email Tool
# -----------------------------
class EmailToolInput(BaseModel):
    subject: str
    body: str
    to: str


@tool(
    "send_email_tool",
    args_schema=EmailToolInput,
    description="Send formatted message via Email",
)
async def send_email_tool(subject: str, body: str, to: str) -> ToolResponse:
    import time

    start_time = time.time()

    # Validate email configuration
    if not all([settings.SMTP_HOST, settings.EMAIL_FROM]):
        return ToolResponse(
            status=ToolStatus.NOT_CONFIGURED,
            message="Email integration not configured",
            error={
                "reason": "missing_configuration",
                "detail": "SMTP host or FROM address not configured",
                "missing_fields": [
                    field for field in ["SMTP_HOST", "EMAIL_FROM"] if not getattr(settings, field, None)
                ],
            },
            meta={"to": to, "subject": subject},
            tool_name="send_email_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=getattr(settings, "SMTP_USE_TLS", True),
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
        )
        return ToolResponse.success(
            message=f"Email sent successfully to {to}",
            data={"recipient": to, "subject": subject, "from": settings.EMAIL_FROM},
            meta={
                "to": to,
                "subject": subject,
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": settings.SMTP_PORT,
                "body_length": len(body),
            },
            tool_name="send_email_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    except Exception as e:
        error_type = type(e).__name__
        return ToolResponse.fail(
            message=f"Failed to send email to {to}",
            error_details={
                "error_type": error_type,
                "error_message": str(e),
                "recipient": to,
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": settings.SMTP_PORT,
            },
            meta={"to": to, "subject": subject},
            tool_name="send_email_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )


# -----------------------------
# API Tool
# -----------------------------
class ApiToolInput(BaseModel):
    payload: dict[str, Any]
    endpoint: str


@tool(
    "send_api_tool",
    args_schema=ApiToolInput,
    description="Send payload to external API",
)
async def send_api_tool(payload: dict[str, Any], endpoint: str) -> ToolResponse:
    import time

    start_time = time.time()

    # Validate endpoint URL
    if not endpoint or not endpoint.startswith(("http://", "https://")):
        return ToolResponse.fail(
            message="Invalid API endpoint URL",
            error_details={
                "reason": "invalid_endpoint",
                "endpoint": endpoint,
                "detail": "Endpoint must be a valid HTTP/HTTPS URL",
            },
            meta={"endpoint": endpoint},
            tool_name="send_api_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )

    try:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
            resp = await client.post(endpoint, json=payload)

            # Determine status based on HTTP response code
            if 200 <= resp.status_code < 300:
                status = ToolStatus.SUCCESS
                message = f"API request successful to {endpoint}"
            elif 400 <= resp.status_code < 500:
                status = ToolStatus.ERROR
                message = f"Client error when calling {endpoint}"
            elif 500 <= resp.status_code < 600:
                status = ToolStatus.ERROR
                message = f"Server error when calling {endpoint}"
            else:
                status = ToolStatus.WARNING
                message = f"Unexpected response code from {endpoint}"

            # Try to parse response JSON if possible
            response_data = None
            try:
                response_data = resp.json()
            except Exception as e:  # noqa
                response_data = resp.text if hasattr(resp, "text") else str(resp.content)

            return ToolResponse(
                status=status,
                message=message,
                data={
                    "response_data": response_data,
                    "status_code": resp.status_code,
                    "headers": dict(resp.headers),
                },
                meta={
                    "endpoint": endpoint,
                    "status_code": resp.status_code,
                    "payload_size": len(str(payload)),
                    "response_size": len(str(response_data)) if response_data else 0,
                },
                tool_name="send_api_tool",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    except httpx.TimeoutException:
        return ToolResponse.fail(
            message=f"Timeout when calling API endpoint {endpoint}",
            error_details={
                "error_type": "TimeoutException",
                "timeout_seconds": settings.HTTP_TIMEOUT,
                "endpoint": endpoint,
            },
            meta={"endpoint": endpoint, "timeout": settings.HTTP_TIMEOUT},
            tool_name="send_api_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    except httpx.RequestError as e:
        return ToolResponse.fail(
            message=f"Request error when calling {endpoint}",
            error_details={
                "error_type": "RequestError",
                "error_message": str(e),
                "endpoint": endpoint,
            },
            meta={"endpoint": endpoint},
            tool_name="send_api_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
    except Exception as e:
        return ToolResponse.fail(
            message=f"Unexpected error when calling {endpoint}",
            error_details={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "endpoint": endpoint,
            },
            meta={"endpoint": endpoint},
            tool_name="send_api_tool",
            execution_time_ms=(time.time() - start_time) * 1000,
        )
