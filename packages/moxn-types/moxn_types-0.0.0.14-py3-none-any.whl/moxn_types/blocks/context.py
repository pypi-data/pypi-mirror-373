from __future__ import annotations

from typing import Any, Literal, Optional, TypedDict

from pydantic import BaseModel, Field

from moxn_types.content import Provider


class OpenAIChatProviderSettings(TypedDict, total=False):
    """OpenAI-specific settings that can be passed to content blocks."""

    image_detail: Optional[Literal["auto", "low", "high"]]


class ProviderSettings(TypedDict, total=False):
    """Provider-specific settings that can be passed to content blocks."""

    openai_chat: OpenAIChatProviderSettings


class MessageContextModel(BaseModel):
    """
    Context object that gets passed down from prompt instance to messages to blocks.
    Contains all necessary context for rendering blocks to provider-specific formats.
    """

    # Current provider being used
    provider: Provider | None = None

    # Variables mapping - used by variable blocks to substitute values
    variables: dict[str, Any] = Field(default_factory=dict)

    # Provider-specific settings
    provider_settings: dict[Provider, ProviderSettings] = Field(default_factory=dict)

    # Additional metadata that might be useful across blocks
    metadata: dict[str, Any] = Field(default_factory=dict)
