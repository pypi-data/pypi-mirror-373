"""Typed domain models for content blocks used in provider conversion."""

from enum import Enum
from pathlib import Path
from typing import Any, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from google.genai.types import File as GoogleFile
else:
    GoogleFile = Any


class BlockType(str, Enum):
    """Content block types."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VARIABLE = "variable"
    SIGNED = "signed"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class VariableType(str, Enum):
    """Variable block sub-types."""
    PRIMITIVE = "primitive"
    IMAGE = "image"
    FILE = "file"


class VariableFormat(str, Enum):
    """Variable display format."""
    INLINE = "inline"
    BLOCK = "block"


class ImageSourceType(str, Enum):
    """Image source types."""
    BASE64 = "base64"
    BYTES = "bytes"
    URL = "url"
    LOCAL_FILE = "local_file"
    GOOGLE_FILE = "google_file"
    GOOGLE_FILE_REFERENCE = "google_file_reference"


class FileSourceType(str, Enum):
    """File source types."""
    BASE64 = "base64"
    BYTES = "bytes"
    URL = "url"
    OPENAI_FILE_REFERENCE = "openai_file_reference"
    GOOGLE_FILE = "google_file"
    GOOGLE_FILE_REFERENCE = "google_file_reference"


# Base classes
class TypedBlockBase(BaseModel):
    """Base class for all typed content blocks."""
    block_type: BlockType
    options: dict[str, Any] = {}
    
    model_config = ConfigDict(populate_by_name=True)


# Text Content
class TextContent(TypedBlockBase):
    """Text content block."""
    block_type: BlockType = BlockType.TEXT
    text: str


# Variable Content
class VariableContent(TypedBlockBase):
    """Variable content block."""
    block_type: BlockType = BlockType.VARIABLE
    name: str
    variable_type: VariableType
    format: VariableFormat
    description: str = ""
    required: bool = True
    default_value: str | None = None


# Image Content
class ImageContent(TypedBlockBase):
    """Image content block."""
    block_type: BlockType = BlockType.IMAGE
    source_type: ImageSourceType
    media_type: str  # e.g., "image/jpeg", "image/png"
    
    # Source-specific fields (only one should be populated based on source_type)
    base64: str | None = None
    bytes_data: bytes | None = None  
    url: str | None = None
    filepath: Path | None = None
    google_file: GoogleFile | None = None
    google_uri: str | None = None


# File Content
class FileContent(TypedBlockBase):
    """File content block."""
    block_type: BlockType = BlockType.FILE
    source_type: FileSourceType
    media_type: str  # e.g., "application/pdf"
    
    # Source-specific fields (only one should be populated based on source_type)
    base64: str | None = None
    bytes_data: bytes | None = None
    url: str | None = None
    openai_file_id: str | None = None
    google_file: GoogleFile | None = None
    google_uri: str | None = None


# Signed URL Content
class SignedURLContent(TypedBlockBase):
    """Signed URL content block."""
    block_type: BlockType = BlockType.SIGNED
    file_path: str
    media_type: str | None = None


# Tool Content (for future extension)
class ToolCallContent(TypedBlockBase):
    """Tool call content block."""
    block_type: BlockType = BlockType.TOOL_CALL
    tool_name: str
    tool_call_id: str
    arguments: dict[str, Any] = {}


class ToolResultContent(TypedBlockBase):
    """Tool result content block."""
    block_type: BlockType = BlockType.TOOL_RESULT
    tool_call_id: str
    result: Any


# Union type for all typed blocks
TypedContentBlock = (
    TextContent
    | VariableContent 
    | ImageContent
    | FileContent
    | SignedURLContent
    | ToolCallContent
    | ToolResultContent
)