"""Raw content block model for flexible API parsing."""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class RawContentBlock(BaseModel):
    """
    Flexible content block model for parsing API responses.
    
    This model is designed to handle any block type from the API without
    breaking on unknown fields or new block types. It captures the common
    structure while allowing extra fields.
    """
    
    # Core fields present in all blocks
    block_type: str = Field(alias="blockType")
    options: dict[str, Any] = Field(default_factory=dict)
    
    # Text block fields
    text: str | None = None
    
    # Variable block fields  
    name: str | None = None
    variable_type: str | None = Field(None, alias="variableType")
    format: str | None = None
    description: str | None = None
    required: bool | None = None
    default_value: str | None = Field(None, alias="defaultValue")
    
    # Image/File source type fields
    type: str | None = None  # For discriminating image/file sources
    
    # Image/File content fields - these vary by source type
    base64: str | None = None
    url: str | None = None
    uri: str | None = None
    filepath: str | None = None
    bytes_data: bytes | None = None  # Renamed to avoid conflict with built-in bytes
    
    # Media type for images/files
    media_type: str | None = Field(None, alias="mediaType")
    
    # Signed URL fields
    file_path: str | None = Field(None, alias="filePath")
    
    # Tool result/call fields (for future extension)
    tool_name: str | None = Field(None, alias="toolName")
    tool_call_id: str | None = Field(None, alias="toolCallId")
    
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Allow extra fields from API
    )
    
    def get_extra_fields(self) -> dict[str, Any]:
        """Get any extra fields not defined in the model."""
        return {k: v for k, v in self.__dict__.items() 
                if k not in self.model_fields}