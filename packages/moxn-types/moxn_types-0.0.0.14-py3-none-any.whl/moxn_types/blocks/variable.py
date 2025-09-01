from enum import Enum
from typing import Annotated, ClassVar, Literal

from pydantic import Field

from moxn_types.blocks.base import BaseContent, BlockType


# 1. Enums
# --------------------------------------------------------------------------- #
class VariableFormat(str, Enum):
    INLINE = "inline"
    BLOCK = "block"


class VariableType(str, Enum):
    """Format of a variable."""

    PRIMITIVE = "primitive"
    IMAGE = "image"
    FILE = "file"


# --------------------------------------------------------------------------- #
# 2. Base Variable class
# --------------------------------------------------------------------------- #


class TextVariableModel(BaseContent):
    """A variable that represents text content."""

    block_type: ClassVar[Literal[BlockType.VARIABLE]] = BlockType.VARIABLE
    name: str
    variable_type: Literal[VariableType.PRIMITIVE] = VariableType.PRIMITIVE
    format: VariableFormat
    description: str = ""
    required: bool = True
    default_value: str | None = None


class ImageVariableModel(BaseContent):
    """A variable that represents image content."""

    block_type: ClassVar[Literal[BlockType.VARIABLE]] = BlockType.VARIABLE
    name: str
    variable_type: Literal[VariableType.IMAGE] = VariableType.IMAGE
    format: VariableFormat
    description: str = ""
    required: bool = True


class FileVariableModel(BaseContent):
    """A variable that represents document content (PDF)."""

    block_type: ClassVar[Literal[BlockType.VARIABLE]] = BlockType.VARIABLE
    name: str
    variable_type: Literal[VariableType.FILE] = VariableType.FILE
    format: VariableFormat
    description: str = ""
    required: bool = True


VariableContentModel = Annotated[
    TextVariableModel | ImageVariableModel | FileVariableModel,
    Field(discriminator="variable_type"),
]
