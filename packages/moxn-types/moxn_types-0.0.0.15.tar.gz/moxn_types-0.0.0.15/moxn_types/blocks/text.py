from typing import ClassVar, Literal

from pydantic import ConfigDict, Field

from moxn_types.blocks.base import BaseContent, BlockType


class TextContentModel(BaseContent):
    block_type: ClassVar[Literal[BlockType.TEXT]] = Field(
        BlockType.TEXT, alias="blockType"
    )
    text: str

    model_config = ConfigDict(populate_by_name=True)
