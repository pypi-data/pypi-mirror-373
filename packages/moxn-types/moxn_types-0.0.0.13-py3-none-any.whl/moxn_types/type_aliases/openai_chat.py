"""Type definitions for OpenAI Chat provider-specific content blocks."""

from typing import TYPE_CHECKING, Sequence, TypedDict, Union

if TYPE_CHECKING:
    # -- OpenAIChat --
    from openai.types.chat import ChatCompletion as OpenAIChatCompletion
    from openai.types.chat import (
        ChatCompletionMessageToolCallParam as OpenAIChatToolUseBlockParam,
    )
    from openai.types.chat.chat_completion_assistant_message_param import (
        ChatCompletionAssistantMessageParam as OpenAIChatAssistantMessageParam,
    )
    from openai.types.chat.chat_completion_content_part_image_param import (
        ChatCompletionContentPartImageParam as OpenAIChatCompletionContentPartImageParam,
    )
    from openai.types.chat.chat_completion_content_part_image_param import (
        ImageURL as OpenAIChatImageURL,
    )
    from openai.types.chat.chat_completion_content_part_param import (
        ChatCompletionContentPartParam as OpenAIChatCompletionContentPartParam,
    )
    from openai.types.chat.chat_completion_content_part_param import (
        File as OpenAIChatFile,
    )
    from openai.types.chat.chat_completion_content_part_param import (
        FileFile as OpenAIChatFileFile,
    )
    from openai.types.chat.chat_completion_content_part_text_param import (
        ChatCompletionContentPartTextParam as OpenAIChatCompletionContentPartTextParam,
    )
    from openai.types.chat.chat_completion_developer_message_param import (
        ChatCompletionDeveloperMessageParam as OpenAIChatDeveloperMessageParam,
    )
    from openai.types.chat.chat_completion_message_tool_call_param import (
        Function as OpenAIChatFunction,
    )
    from openai.types.chat.chat_completion_system_message_param import (
        ChatCompletionSystemMessageParam as OpenAIChatSystemMessageParam,
    )
    from openai.types.chat.chat_completion_tool_message_param import (
        ChatCompletionToolMessageParam as OpenAIChatToolResponseParam,
    )
    from openai.types.chat.chat_completion_user_message_param import (
        ChatCompletionUserMessageParam as OpenAIChatUserMessageParam,
    )
else:
    OpenAIChatToolUseBlockParam = dict
    OpenAIChatToolResponseParam = dict
    OpenAIChatCompletionContentPartParam = dict
    OpenAIChatCompletionContentPartImageParam = dict
    OpenAIChatImageURL = dict
    OpenAIChatFile = dict
    OpenAIChatFileFile = dict
    OpenAIChatToolUseBlockParam = dict
    OpenAIChatToolResponseParam = dict
    OpenAIChatCompletionContentPartTextParam = dict
    OpenAIChatFunction = dict
    OpenAIChatAssistantMessageParam = dict
    OpenAIChatDeveloperMessageParam = dict
    OpenAIChatSystemMessageParam = dict
    OpenAIChatUserMessageParam = dict
    try:
        from openai.types.chat import ChatCompletion as OpenAIChatCompletion
    except ImportError:
        pass

# OpenAI content block types
OpenAIChatContentBlock = Union[
    OpenAIChatCompletionContentPartParam,
    OpenAIChatCompletionContentPartImageParam,
    OpenAIChatToolUseBlockParam,
    OpenAIChatToolResponseParam,
]

# Provider-specific block sequences (for grouping operations)
OpenAIChatContentBlockSequence = Sequence[Sequence[OpenAIChatContentBlock]]


class OpenAIChatMessagesParam(TypedDict):
    messages: list[OpenAIChatContentBlock]
