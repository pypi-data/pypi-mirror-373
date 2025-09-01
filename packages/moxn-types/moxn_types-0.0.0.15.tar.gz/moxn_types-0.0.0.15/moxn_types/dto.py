from typing import Sequence

from pydantic import ConfigDict, Field

from moxn_types.base import BasePrompt, BaseSchema, BaseTask, MessageBase
from moxn_types.blocks.content_block import ContentBlockModel


class MessageDTO(MessageBase[ContentBlockModel]):
    """Message DTO for API communication - blocks are raw dicts."""

    blocks: Sequence[Sequence[ContentBlockModel]] = Field(
        repr=False, default_factory=list
    )

    model_config = ConfigDict(populate_by_name=True)


class SchemaDTO(BaseSchema):
    model_config = ConfigDict(populate_by_name=True)


class PromptDTO(BasePrompt[MessageDTO, SchemaDTO]):
    """Prompt DTO for API communication."""

    messages: Sequence[MessageDTO] = Field(default_factory=list)
    input_schema: SchemaDTO = Field(..., alias="inputSchema")

    model_config = ConfigDict(populate_by_name=True)


class TaskDTO(BaseTask[PromptDTO, SchemaDTO]):
    """Task DTO for API communication."""

    prompts: Sequence[PromptDTO] = Field(default_factory=list)
    schemas: list[SchemaDTO] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
