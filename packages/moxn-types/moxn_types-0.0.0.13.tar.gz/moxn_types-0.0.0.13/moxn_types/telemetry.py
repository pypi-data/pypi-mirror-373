from datetime import datetime
from enum import Enum
from typing import Any, Generic, Literal, Optional, Protocol, TypeAlias, TypeVar, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from moxn_types.content import Provider
from moxn_types.base import MessageBase, RenderableModel
from moxn_types.dto import MessageDTO
from moxn_types.response import ParsedResponseModelBase


# Core Domain Types
class SpanKind(str, Enum):
    LLM = "llm"
    TOOL = "tool"
    AGENT = "agent"


class SpanStatus(str, Enum):
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


class SpanLogType(str, Enum):
    START = "span_start"
    END = "span_end"
    ERROR = "span_error"


class SpanEventLogType(str, Enum):
    EVENT = "span_event"
    ERROR = "span_event_error"


class BaseTelemetryLogRequest(BaseModel):
    id: UUID
    timestamp: datetime | None = None
    prompt_id: UUID
    prompt_version_id: UUID
    message: str | None = None
    log_metadata: dict[str, Any] = Field(default_factory=dict)
    attributes: dict[str, Any] = Field(default_factory=dict)
    attributes_key: str | None = None


class SpanLogRequest(BaseTelemetryLogRequest):
    span_id: UUID
    root_span_id: UUID
    parent_span_id: UUID | None = None
    event_type: SpanLogType


class SpanEventLogRequest(BaseTelemetryLogRequest):
    span_id: UUID
    span_event_id: UUID
    event_type: SpanEventLogType


# Base Models
class BaseTelemetryEvent(BaseModel):
    """Base class for all telemetry events"""

    model_config = ConfigDict(
        json_encoders={
            UUID: str,  # Ensure UUIDs are serialized as strings
            datetime: lambda dt: dt.isoformat(),  # Ensure datetimes are ISO format
        }
    )

    id: UUID
    timestamp: datetime
    prompt_id: UUID
    prompt_version_id: UUID
    message: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class BaseSpanLog(BaseTelemetryEvent):
    """Base class for span logs"""

    span_id: UUID
    root_span_id: UUID
    parent_span_id: Optional[UUID] = None
    event_type: SpanLogType


class BaseSpanEventLog(BaseTelemetryEvent):
    """Base class for span event logs"""

    span_id: UUID
    span_event_id: UUID
    event_type: SpanEventLogType


class TelemetryLogResponse(BaseModel):
    """Response from telemetry log endpoint"""

    id: UUID
    timestamp: datetime
    status: str = "success"
    message: Optional[str] = None


class BaseSpan(BaseTelemetryEvent):
    """Base class for span-related events"""

    span_id: UUID
    name: str
    kind: SpanKind
    status: SpanStatus = SpanStatus.UNSET
    root_span_id: Optional[UUID] = None
    parent_span_id: Optional[UUID] = None


class BaseSpanEvent(BaseTelemetryEvent):
    """Base class for span event-related events"""

    span_id: UUID
    event_type: Literal["llm_response"]
    variables: Optional[dict[str, Any]] = None
    messages: Optional[list[dict[str, Any]]] = None
    llm_response_content: Optional[str] = None
    llm_response_tool_calls: Optional[list[dict[str, Any]]] = None


# Domain Events
class SpanCreated(BaseSpan):
    """Event emitted when a span is created"""

    pass


class SpanCompleted(BaseSpan):
    """Event emitted when a span is completed"""

    pass


class SpanFailed(BaseSpan):
    """Event emitted when a span fails"""

    error: str


class SpanResponse(BaseModel):
    span_id: UUID
    status: str = "success"
    message: Optional[str] = None


class SpanEventResponse(BaseModel):
    event_id: UUID
    span_id: UUID
    event_type: str
    status: str = "success"
    message: Optional[str] = None


class LLMSpanEvent(BaseSpanEvent):
    """Event emitted for LLM interactions"""

    provider: Provider
    raw_input: Optional[dict[str, Any]] = None
    rendered_input: Optional[dict[str, Any]] = None


class CreateSpanRequest(BaseSpan):
    """API prompt model for span creation"""

    pass


class CreateSpanEventRequest(BaseSpanEvent):
    """API prompt model for span event creation"""

    pass


class TelemetryResponse(BaseTelemetryEvent):
    """Base API response model"""

    status: str = "success"


class ErrorResponse(BaseTelemetryEvent):
    """API error response model"""

    status: str = "error"
    error_message: str


# --- Type Aliases ---
TelemetryLogRequest: TypeAlias = Union[SpanLogRequest, SpanEventLogRequest]


class Entity(BaseModel):
    entity_type: str
    entity_id: UUID
    entity_version_id: UUID | None = None


class SignedURLRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    file_path: str
    entity: Entity | None = None
    log_request: TelemetryLogRequest
    media_type: Literal[
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "application/json",
    ]
    prompt_id: UUID | None = None
    prompt_version_id: UUID | None = None


class SignedURLResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: str
    file_path: str
    expiration: datetime
    message: str = "Signed URL generated successfully"


MAX_INLINE_ATTRIBUTES_SIZE = 1  # 10 * 1024  # 10KB threshold for inline attributes


# Transport Protocol
class TelemetryTransport(Protocol):
    """Protocol for sending telemetry data"""

    async def send_log(
        self, log_request: Union[SpanLogRequest, SpanEventLogRequest]
    ) -> TelemetryLogResponse: ...

    async def send_telemetry_log_and_get_signed_url(
        self, log_request: SignedURLRequest
    ) -> SignedURLResponse: ...


ParsedResponseT = TypeVar("ParsedResponseT", bound=ParsedResponseModelBase)
MessageT = TypeVar("MessageT", bound=MessageBase)


class LLMEventModelBase(BaseModel, Generic[ParsedResponseT, MessageT]):
    """Domain model for LLM interactions"""

    prompt_id: UUID = Field(..., alias="promptId")
    prompt_version_id: UUID = Field(..., alias="promptVersionId")
    messages: list[MessageT] = Field(..., alias="messages")
    provider: Provider | None = Field(default=None, alias="provider")
    raw_response: dict[str, Any] = Field(..., alias="rawResponse")
    parsed_response: ParsedResponseT
    session_data: RenderableModel | None = Field(default=None, alias="sessionData")
    rendered_input: Optional[dict[str, Any]] = Field(
        default=None, alias="renderedInput"
    )
    attributes: Optional[dict[str, Any]] = Field(default=None, alias="attributes")

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class LLMEventModel(LLMEventModelBase[ParsedResponseModelBase, MessageDTO]):
    """Domain model for LLM interactions"""

    messages: list[MessageDTO] = Field(..., alias="messages")
    parsed_response: ParsedResponseModelBase = Field(..., alias="parsedResponse")
