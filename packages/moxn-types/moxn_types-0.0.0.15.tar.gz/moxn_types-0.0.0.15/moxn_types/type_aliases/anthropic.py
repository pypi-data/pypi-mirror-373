"""Type definitions for Anthropic provider-specific content blocks."""

from typing import TYPE_CHECKING, Sequence, TypedDict, Union

if TYPE_CHECKING:
    # -- Anthropic --
    from anthropic.types import (
        Base64ImageSourceParam as AnthropicBase64ImageSourceParam,
    )
    from anthropic.types import (
        Base64PDFSourceParam as AnthropicBase64PDFSourceParam,
    )
    from anthropic.types import (
        DocumentBlockParam as AnthropicFileBlockParam,
    )
    from anthropic.types import (
        ImageBlockParam as AnthropicImageBlockParam,
    )
    from anthropic.types import Message as AnthropicMessage
    from anthropic.types import (
        TextBlockParam as AnthropicTextBlockParam,
    )
    from anthropic.types import (
        ToolResultBlockParam as AnthropicToolResultBlockParam,
    )
    from anthropic.types import (
        ToolUseBlockParam as AnthropicToolUseBlockParam,
    )
    from anthropic.types import URLImageSourceParam as AnthropicURLImageSourceParam
    from anthropic.types import (
        URLPDFSourceParam as AnthropicURLPDFSourceParam,
    )
    from anthropic.types.cache_control_ephemeral_param import (
        CacheControlEphemeralParam as AnthropicCacheControlEphemeralParam,
    )
    from anthropic.types.content_block import ContentBlock as AnthropicContentBlock
    from anthropic.types.message_param import MessageParam as AnthropicMessageParam
    from anthropic.types.tool_result_block_param import Content as AnthropicContent
    from anthropic.types.tool_use_block import ToolUseBlock as AnthropicToolUseBlock
else:
    AnthropicBase64PDFSourceParam = dict
    AnthropicURLPDFSourceParam = dict
    AnthropicBase64ImageSourceParam = dict
    AnthropicURLImageSourceParam = dict
    AnthropicFileBlockParam = dict
    AnthropicImageBlockParam = dict
    AnthropicMessageParam = dict
    AnthropicTextBlockParam = dict
    AnthropicToolUseBlockParam = dict
    AnthropicToolResultBlockParam = dict
    AnthropicCacheControlEphemeralParam = dict
    AnthropicContent = dict
    try:
        from anthropic.types.content_block import ContentBlock as AnthropicContentBlock
        from anthropic.types.message import Message as AnthropicMessage
        from anthropic.types.tool_use_block import ToolUseBlock as AnthropicToolUseBlock
    except ImportError:
        pass

# Anthropic content block types
AnthropicContentBlockParam = Union[
    AnthropicTextBlockParam,
    AnthropicImageBlockParam,
    AnthropicFileBlockParam,
    AnthropicToolUseBlockParam,
    AnthropicToolResultBlockParam,
]

AnthropicSystemContentBlockParam = AnthropicTextBlockParam
AnthropicDocumentSourceBlock = (
    AnthropicBase64PDFSourceParam | AnthropicURLPDFSourceParam
)
AnthropicImageSourceBlockParam = (
    AnthropicBase64ImageSourceParam | AnthropicURLImageSourceParam
)


# Provider-specific block sequences (for grouping operations)
AnthropicContentBlockParamSequence = Sequence[Sequence[AnthropicContentBlockParam]]
AnthropicSystemContentBlockParamSequence = Sequence[
    Sequence[AnthropicSystemContentBlockParam]
]


class AnthropicMessagesParam(TypedDict, total=False):
    system: str | list[AnthropicSystemContentBlockParam]
    messages: list[AnthropicContentBlockParam]
