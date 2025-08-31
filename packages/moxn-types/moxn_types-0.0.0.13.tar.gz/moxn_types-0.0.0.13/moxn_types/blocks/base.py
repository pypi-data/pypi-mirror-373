from enum import Enum
from typing import Any

from pydantic import BaseModel


class BlockType(Enum):
    FILE = "file"
    IMAGE = "image"
    TEXT = "text"
    VARIABLE = "variable"
    SIGNED = "signed"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class BaseContent(BaseModel):
    options: dict[str, Any] = {}
