"""
Module for parsing and normalizing LLM responses across different providers.
"""

from enum import Enum
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
)
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from moxn_types.blocks.text import TextContentModel
from moxn_types.blocks.tool import ToolCallModel
from moxn_types.content import Provider


class StopReason(str, Enum):
    """Normalized stop reasons across providers."""

    END_TURN = "end_turn"  # Normal completion
    MAX_TOKENS = "max_tokens"  # Max tokens reached
    TOOL_CALL = "tool_call"  # Model wants to call a tool
    CONTENT_FILTER = "content_filter"  # Content was filtered for safety reasons
    ERROR = "error"  # Some error occurred
    OTHER = "other"  # Other reason


class TokenUsage(BaseModel):
    """Normalized token usage across providers."""

    input_tokens: int | None = None
    thinking_tokens: int | None = None
    completion_tokens: int | None = None


class ResponseMetadata(BaseModel):
    """Normalized response metadata across providers."""

    normalized_finish_reason: StopReason
    raw_finish_reason: str


# Generic type parameters for text content and tool calls
TextContentT = TypeVar("TextContentT", bound=TextContentModel, covariant=True)
ToolCallT = TypeVar("ToolCallT", bound=ToolCallModel, covariant=True)


class ParsedResponseCandidateModelBase(BaseModel, Generic[TextContentT, ToolCallT]):
    """Normalized response candidate with content blocks and metadata."""

    content_blocks: list[TextContentT | ToolCallT]
    metadata: ResponseMetadata


class ParsedResponseCandidateModel(
    ParsedResponseCandidateModelBase[TextContentModel, ToolCallModel]
):
    """Normalized response candidate with content blocks and metadata."""

    content_blocks: list[TextContentModel | ToolCallModel]
    metadata: ResponseMetadata


ParsedResponseCandidateModelT = TypeVar(
    "ParsedResponseCandidateModelT", bound=ParsedResponseCandidateModelBase
)


class ParsedResponseModelBase(BaseModel, Generic[ParsedResponseCandidateModelT]):
    """
    Normalized response content from any LLM provider.

    Contains parsed content blocks, metadata, and original response for reference.
    """

    id: UUID = Field(default_factory=uuid4)
    provider: Provider
    candidates: list[ParsedResponseCandidateModelT]
    stop_reason: StopReason = Field(
        ...,
        description="Normalized stop reason - from first candidate if multiple candidates",
    )
    usage: TokenUsage = Field(
        default_factory=TokenUsage,
        description="Token usage from parent objects, candidate token usage in candidate metadata if available",
    )
    model: str | None = None
    raw_response: dict | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


ResponseType = TypeVar("ResponseType", contravariant=True)
ParsedResponseModelT = TypeVar(
    "ParsedResponseModelT", bound=ParsedResponseModelBase, covariant=True
)


class ResponseParserProtocol(Protocol, Generic[ResponseType, ParsedResponseModelT]):
    """Protocol for provider-specific response parsers."""

    @classmethod
    def parse_response(
        cls, response: ResponseType, provider: Provider
    ) -> ParsedResponseModelT: ...

    @classmethod
    def extract_metadata(cls, response: ResponseType) -> dict[str, Any]: ...
