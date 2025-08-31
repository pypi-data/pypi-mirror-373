"""Response types for git-based API operations."""

from datetime import datetime
from typing import Generic, TypeVar, Dict
from typing_extensions import TypedDict
from uuid import UUID

from pydantic import BaseModel, Field

from moxn_types.content import MessageRole, Author
from moxn_types.blocks.content_block import ContentBlockModel
from moxn_types.dto import TaskDTO, PromptDTO, SchemaDTO, MessageDTO
from moxn_types.base import Branch, Commit


T = TypeVar("T")


class MoxnSchemaMetadata(BaseModel):
    """Metadata embedded in JSON Schema x-moxn-metadata field."""
    schema_id: UUID
    schema_version_id: UUID | None = None
    prompt_id: UUID
    prompt_version_id: UUID | None = None
    task_id: UUID
    branch_id: UUID | None = None  # Can be None in API responses
    commit_id: str | None = None
    
    model_config = {"populate_by_name": True}


class JsonSchemaDefinition(BaseModel):
    """Full JSON Schema definition with embedded Moxn metadata."""
    type: str
    title: str | None = None
    description: str | None = None
    properties: dict = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)
    x_moxn_metadata: MoxnSchemaMetadata = Field(alias="x-moxn-metadata")
    
    # Additional JSON Schema fields (extensible) - allow any other fields
    model_config = {"populate_by_name": True, "extra": "allow"}


# TypedDict for schema definitions dictionary
SchemaDefinitions = Dict[str, JsonSchemaDefinition]


class PromptAtCommit(BaseModel):
    """Prompt snapshot at a specific commit."""
    prompt_id: UUID = Field(..., alias="promptId")  # Anchor ID (stable)
    commit_id: str = Field(..., alias="commitId")   # Snapshot ID
    name: str
    description: str
    task_id: UUID = Field(..., alias="taskId")
    created_at: datetime = Field(..., alias="createdAt")
    messages: list["MessageAtCommit"]
    message_order: list[UUID] = Field(default_factory=list, alias="messageOrder")
    
    model_config = {"populate_by_name": True}


class MessageAtCommit(BaseModel):
    """Message snapshot at a specific commit."""
    message_id: UUID = Field(..., alias="messageId")  # Anchor ID (stable)
    commit_id: str = Field(..., alias="commitId")     # Snapshot ID
    name: str
    description: str
    author: Author
    role: MessageRole
    blocks: list[list[ContentBlockModel]] = Field(default_factory=list)
    
    model_config = {"populate_by_name": True}


class TaskSnapshot(BaseModel):
    """Complete task state at a commit."""
    task_id: UUID = Field(..., alias="taskId")
    commit_id: str = Field(..., alias="commitId")
    name: str
    description: str
    created_at: datetime = Field(..., alias="createdAt")
    prompts: list[PromptAtCommit] = Field(default_factory=list)
    
    model_config = {"populate_by_name": True}


class EntityResponse(BaseModel, Generic[T]):
    """Generic response wrapper for any entity with metadata."""
    data: T
    commit_id: str = Field(..., alias="commitId")
    branch_name: str | None = Field(None, alias="branchName")
    is_deleted: bool = Field(False, alias="isDeleted")
    
    model_config = {"populate_by_name": True}


class TaskMetadata(BaseModel):
    """Metadata for task responses."""
    branch_id: UUID | None = Field(None, alias="branchId")
    commit_id: str | None = Field(None, alias="commitId")
    last_commit: str | None = Field(None, alias="lastCommit")
    
    model_config = {"populate_by_name": True}


class PromptMetadata(BaseModel):
    """Metadata for prompt responses."""
    commit_id: str | None = Field(None, alias="commitId")
    
    model_config = {"populate_by_name": True}


class TaskFullState(BaseModel):
    """Full task state with proper DTO objects."""
    # Task fields - inherits from BaseTask via composition
    id: UUID
    name: str
    description: str
    branch_id: UUID | None = Field(None, alias="branchId")
    commit_id: str | None = Field(None, alias="commitId")
    last_commit: Commit | None = Field(None, alias="lastCommit")
    
    # Collections using proper DTO objects
    prompts: list[PromptDTO] = Field(default_factory=list)
    definitions: SchemaDefinitions = Field(default_factory=dict)
    branches: list[Branch] = Field(default_factory=list)
    
    model_config = {"populate_by_name": True}
    
    def to_codegen_payload(self) -> dict:
        """
        Convert task definitions to code generation payload.
        
        Returns:
            Dictionary format expected by MoxnSchemaGenerator
        """
        return {
            "definitions": {
                name: definition.model_dump(by_alias=True)
                for name, definition in self.definitions.items()
            }
        }


class PromptFullState(BaseModel):
    """Full prompt state with proper DTO objects."""
    # Prompt fields - inherits from BasePrompt via composition
    id: UUID
    name: str 
    description: str
    task_id: UUID | None = Field(None, alias="taskId")
    commit_id: str | None = Field(None, alias="commitId")
    
    # Collections using proper DTO objects
    messages: list[MessageDTO] = Field(default_factory=list)
    input_schema: SchemaDTO = Field(..., alias="inputSchema")
    
    model_config = {"populate_by_name": True}


class SchemaFullState(BaseModel):
    """Full schema state with proper DTO objects."""
    # Schema fields - inherits from BaseSchema via composition  
    id: UUID
    name: str
    description: str
    exportedJSON: str
    branch_id: UUID | None = Field(None, alias="branchId")
    commit_id: str | None = Field(None, alias="commitId")
    
    # Additional metadata (if any from API)
    properties: list = Field(default_factory=list)  # May not be used
    
    model_config = {"populate_by_name": True}