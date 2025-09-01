from typing import Sequence

from moxn_types.type_aliases.anthropic import AnthropicContentBlockParam
from moxn_types.type_aliases.google import GoogleContentBlock
from moxn_types.type_aliases.openai_chat import OpenAIChatContentBlock

ProviderContentBlock = (
    AnthropicContentBlockParam | OpenAIChatContentBlock | GoogleContentBlock
)


ProviderContentBlockSequence = (
    Sequence[Sequence[AnthropicContentBlockParam]]
    | Sequence[Sequence[OpenAIChatContentBlock]]
    | Sequence[Sequence[GoogleContentBlock]]
)
