"""Type definitions for Google provider-specific content blocks."""

from typing import TYPE_CHECKING, Sequence, TypedDict, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    # -- Google --
    from google.genai.types import (
        Candidate as GoogleGenerateContentResponseCandidate,
    )
    from google.genai.types import Content as GoogleContent
    from google.genai.types import File as GoogleFile
    from google.genai.types import FunctionCall as GoogleFunctionCall
    from google.genai.types import FunctionResponse as GoogleFunctionResponse
    from google.genai.types import (
        GenerateContentResponse as GoogleGenerateContentResponse,
    )
    from google.genai.types import Part as GooglePart
else:
    GoogleContent = dict
    GoogleFile = dict
    GoogleFunctionCall = dict
    GoogleFunctionResponse = dict
    GooglePart = dict
    GoogleGenerateContentResponse = BaseModel
try:
    from google.genai.types import (
        Candidate as GoogleGenerateContentResponseCandidate,
    )
    from google.genai.types import Content as GoogleContent
    from google.genai.types import File as GoogleFile
    from google.genai.types import FunctionCall as GoogleFunctionCall
    from google.genai.types import FunctionResponse as GoogleFunctionResponse
    from google.genai.types import (
        GenerateContentResponse as GoogleGenerateContentResponse,
    )
    from google.genai.types import Part as GooglePart
except ImportError:
    pass


# Google content block types
GoogleContentBlock = Union[
    GooglePart,
    GoogleFile,
    GoogleFunctionCall,
    GoogleFunctionResponse,
]

GoogleSystemContentBlock = Union[
    GooglePart,
    GoogleFile,
]

# Provider-specific block sequences (for grouping operations)
GoogleContentBlockSequence = Sequence[Sequence[GoogleContentBlock]]
GoogleSystemContentBlockSequence = Sequence[Sequence[GoogleSystemContentBlock]]


class GoogleMessagesParam(TypedDict, total=False):
    system_instruction: str
    content: Sequence[GoogleContent | GoogleFile]
