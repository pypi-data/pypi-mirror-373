"""Block conversion between raw API blocks and typed domain models."""

from pathlib import Path
from typing import Any

from moxn_types.blocks.raw_block import RawContentBlock
from moxn_types.blocks.typed_blocks import (
    BlockType,
    FileContent,
    FileSourceType,
    ImageContent,
    ImageSourceType,
    SignedURLContent,
    TextContent,
    ToolCallContent,
    ToolResultContent,
    TypedContentBlock,
    VariableContent,
    VariableFormat,
    VariableType,
)


class BlockConversionError(Exception):
    """Raised when block conversion fails."""
    pass


def to_typed_block(raw: RawContentBlock) -> TypedContentBlock:
    """
    Convert a raw content block from API to a typed domain model.
    
    Args:
        raw: Raw content block from API
        
    Returns:
        Typed content block for use in provider conversions
        
    Raises:
        BlockConversionError: If conversion fails
    """
    try:
        match raw.block_type:
            case BlockType.TEXT:
                return _convert_text_block(raw)
            case BlockType.VARIABLE:
                return _convert_variable_block(raw)
            case BlockType.IMAGE:
                return _convert_image_block(raw)
            case BlockType.FILE:
                return _convert_file_block(raw)
            case BlockType.SIGNED:
                return _convert_signed_block(raw)
            case BlockType.TOOL_CALL:
                return _convert_tool_call_block(raw)
            case BlockType.TOOL_RESULT:
                return _convert_tool_result_block(raw)
            case _:
                raise BlockConversionError(f"Unknown block type: {raw.block_type}")
                
    except Exception as e:
        raise BlockConversionError(
            f"Failed to convert {raw.block_type} block: {e}"
        ) from e


def from_typed_block(typed: TypedContentBlock) -> RawContentBlock:
    """
    Convert a typed domain model back to a raw content block for API.
    
    Args:
        typed: Typed content block
        
    Returns:
        Raw content block for API serialization
    """
    # Create base raw block
    raw_data = {
        "blockType": typed.block_type.value,
        "options": typed.options,
    }
    
    match typed.block_type:
        case BlockType.TEXT:
            raw_data["text"] = typed.text
            
        case BlockType.VARIABLE:
            raw_data.update({
                "name": typed.name,
                "variableType": typed.variable_type.value,
                "format": typed.format.value,
                "description": typed.description,
                "required": typed.required,
            })
            if typed.default_value is not None:
                raw_data["defaultValue"] = typed.default_value
                
        case BlockType.IMAGE:
            raw_data.update({
                "type": typed.source_type.value,
                "mediaType": typed.media_type,
            })
            # Add source-specific fields
            if typed.base64:
                raw_data["base64"] = typed.base64
            elif typed.url:
                raw_data["url"] = typed.url
            elif typed.filepath:
                raw_data["filepath"] = str(typed.filepath)
            elif typed.google_uri:
                raw_data["uri"] = typed.google_uri
            # Note: bytes and google_file are not serializable to API
            
        case BlockType.FILE:
            raw_data.update({
                "type": typed.source_type.value,
                "mediaType": typed.media_type,
            })
            # Add source-specific fields
            if typed.base64:
                raw_data["base64"] = typed.base64
            elif typed.url:
                raw_data["url"] = typed.url
            elif typed.openai_file_id:
                raw_data["openaiFileId"] = typed.openai_file_id
            elif typed.google_uri:
                raw_data["uri"] = typed.google_uri
                
        case BlockType.SIGNED:
            raw_data["filePath"] = typed.file_path
            if typed.media_type:
                raw_data["mediaType"] = typed.media_type
                
        case BlockType.TOOL_CALL:
            raw_data.update({
                "toolName": typed.tool_name,
                "toolCallId": typed.tool_call_id,
                "arguments": typed.arguments,
            })
            
        case BlockType.TOOL_RESULT:
            raw_data.update({
                "toolCallId": typed.tool_call_id,
                "result": typed.result,
            })
    
    return RawContentBlock(**raw_data)


def _convert_text_block(raw: RawContentBlock) -> TextContent:
    """Convert raw text block to typed text content."""
    if not raw.text:
        raise BlockConversionError("Text block missing required 'text' field")
    
    return TextContent(
        text=raw.text,
        options=raw.options,
    )


def _convert_variable_block(raw: RawContentBlock) -> VariableContent:
    """Convert raw variable block to typed variable content."""
    if not raw.name:
        raise BlockConversionError("Variable block missing required 'name' field")
    if not raw.variable_type:
        raise BlockConversionError("Variable block missing required 'variable_type' field")
    if not raw.format:
        raise BlockConversionError("Variable block missing required 'format' field")
    
    try:
        variable_type = VariableType(raw.variable_type)
        format_type = VariableFormat(raw.format)
    except ValueError as e:
        raise BlockConversionError(f"Invalid variable type or format: {e}")
    
    return VariableContent(
        name=raw.name,
        variable_type=variable_type,
        format=format_type,
        description=raw.description or "",
        required=raw.required if raw.required is not None else True,
        default_value=raw.default_value,
        options=raw.options,
    )


def _convert_image_block(raw: RawContentBlock) -> ImageContent:
    """Convert raw image block to typed image content."""
    if not raw.type:
        raise BlockConversionError("Image block missing required 'type' field")
    if not raw.media_type:
        raise BlockConversionError("Image block missing required 'media_type' field")
    
    try:
        source_type = ImageSourceType(raw.type)
    except ValueError as e:
        raise BlockConversionError(f"Invalid image source type: {e}")
    
    # Validate required fields based on source type
    image_content = ImageContent(
        source_type=source_type,
        media_type=raw.media_type,
        options=raw.options,
    )
    
    # Set source-specific fields
    match source_type:
        case ImageSourceType.BASE64:
            if not raw.base64:
                raise BlockConversionError("base64 image missing 'base64' field")
            image_content.base64 = raw.base64
        case ImageSourceType.BYTES:
            if not raw.bytes_data:
                raise BlockConversionError("bytes image missing 'bytes_data' field")
            image_content.bytes_data = raw.bytes_data
        case ImageSourceType.URL:
            if not raw.url:
                raise BlockConversionError("URL image missing 'url' field")
            image_content.url = raw.url
        case ImageSourceType.LOCAL_FILE:
            if not raw.filepath:
                raise BlockConversionError("local file image missing 'filepath' field")
            image_content.filepath = Path(raw.filepath)
        case ImageSourceType.GOOGLE_FILE_REFERENCE:
            if not raw.uri:
                raise BlockConversionError("Google file reference missing 'uri' field")
            image_content.google_uri = raw.uri
        # GOOGLE_FILE requires the actual file object, handled elsewhere
            
    return image_content


def _convert_file_block(raw: RawContentBlock) -> FileContent:
    """Convert raw file block to typed file content."""
    if not raw.type:
        raise BlockConversionError("File block missing required 'type' field")
    if not raw.media_type:
        raise BlockConversionError("File block missing required 'media_type' field")
    
    try:
        source_type = FileSourceType(raw.type)
    except ValueError as e:
        raise BlockConversionError(f"Invalid file source type: {e}")
    
    file_content = FileContent(
        source_type=source_type,
        media_type=raw.media_type,
        options=raw.options,
    )
    
    # Set source-specific fields
    match source_type:
        case FileSourceType.BASE64:
            if not raw.base64:
                raise BlockConversionError("base64 file missing 'base64' field")
            file_content.base64 = raw.base64
        case FileSourceType.BYTES:
            if not raw.bytes_data:
                raise BlockConversionError("bytes file missing 'bytes_data' field")  
            file_content.bytes_data = raw.bytes_data
        case FileSourceType.URL:
            if not raw.url:
                raise BlockConversionError("URL file missing 'url' field")
            file_content.url = raw.url
        case FileSourceType.GOOGLE_FILE_REFERENCE:
            if not raw.uri:
                raise BlockConversionError("Google file reference missing 'uri' field")
            file_content.google_uri = raw.uri
        # Other types handled elsewhere
            
    return file_content


def _convert_signed_block(raw: RawContentBlock) -> SignedURLContent:
    """Convert raw signed URL block to typed signed URL content."""
    if not raw.file_path:
        raise BlockConversionError("Signed URL block missing required 'file_path' field")
    
    return SignedURLContent(
        file_path=raw.file_path,
        media_type=raw.media_type,
        options=raw.options,
    )


def _convert_tool_call_block(raw: RawContentBlock) -> ToolCallContent:
    """Convert raw tool call block to typed tool call content."""
    if not raw.tool_name:
        raise BlockConversionError("Tool call block missing required 'tool_name' field")
    if not raw.tool_call_id:
        raise BlockConversionError("Tool call block missing required 'tool_call_id' field")
    
    return ToolCallContent(
        tool_name=raw.tool_name,
        tool_call_id=raw.tool_call_id,
        arguments=getattr(raw, 'arguments', {}),
        options=raw.options,
    )


def _convert_tool_result_block(raw: RawContentBlock) -> ToolResultContent:
    """Convert raw tool result block to typed tool result content."""
    if not raw.tool_call_id:
        raise BlockConversionError("Tool result block missing required 'tool_call_id' field")
    
    return ToolResultContent(
        tool_call_id=raw.tool_call_id,
        result=getattr(raw, 'result', None),
        options=raw.options,
    )