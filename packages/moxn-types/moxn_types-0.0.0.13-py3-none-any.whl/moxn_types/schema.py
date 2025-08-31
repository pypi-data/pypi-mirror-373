from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from moxn_types.sentinel import NOT_GIVEN, BaseModelWithOptionalFields, NotGivenOr


# Define Schema types as proper enums to match OpenAPI compatibility
class SchemaPropertyType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    REFERENCE = "reference"  # Custom extension for references


class SchemaPropertyFormat(str, Enum):
    TEXT = "text"
    DATE = "date"
    DATETIME = "date-time"
    EMAIL = "email"
    URI = "uri"
    UUID = "uuid"
    HOSTNAME = "hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    BINARY = "binary"


# Updated to match OpenAPI spec and TypeScript interface
class SchemaPropertyConstraints(BaseModel):
    # Common
    nullable: bool | None = None
    enum: list[Any] | None = None
    default: Any | None = None

    # String constraints
    minLength: int | None = None
    maxLength: int | None = None
    pattern: str | None = None
    format: SchemaPropertyFormat | None = None

    # Number constraints
    minimum: int | float | None = None
    maximum: int | float | None = None
    exclusiveMinimum: bool | None = None
    exclusiveMaximum: bool | None = None
    multipleOf: int | float | None = None

    # Array constraints
    minItems: int | None = None
    maxItems: int | None = None
    uniqueItems: bool | None = None

    # Object constraints
    additionalProperties: bool | None = None
    required: list[str] | None = None

    # Variable Display
    displayMode: str | None = None  # 'inline' | 'block'


class SchemaReference(BaseModel):
    messageId: str
    schemaName: str
    reference: str
    ref: str | None = Field(None, alias="$ref")  # OpenAPI style reference
    isSelfReference: bool | None = None


class SchemaProperty(BaseModelWithOptionalFields):
    name: str
    type: SchemaPropertyType
    description: str
    required: NotGivenOr[bool] = NOT_GIVEN
    properties: NotGivenOr[list["SchemaProperty"]] = NOT_GIVEN  # For object type
    items: NotGivenOr[Optional["SchemaProperty"]] = (
        NOT_GIVEN  # For array type (singular)
    )
    constraints: NotGivenOr[SchemaPropertyConstraints] = NOT_GIVEN
    schemaRef: NotGivenOr[SchemaReference] = (
        NOT_GIVEN  # Updated to use SchemaReference class
    )
    defaultContent: NotGivenOr[Any] = NOT_GIVEN


class Schema(BaseModel):
    name: str
    description: str | None = None
    type: Literal["object"] | None = None  # Default type for top-level schemas
    properties: list[SchemaProperty]
    required: list[str] | None = None  # OpenAPI required property names
    strict: bool = False


class SchemaPromptType(str, Enum):
    ALL = "all"
    INPUT = "input"
    OUTPUT = "output"


class MessageType(str, Enum):
    PROMPT = "message"
    SCHEMA_INPUT = "input"
    SCHEMA_OUTPUT = "output"


class SchemaWithMetadata(BaseModel):
    moxn_schema: Schema = Field(alias="schema")
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    message_id: str = Field(alias="messageId")
    message_version_id: str = Field(alias="messageVersionId")
    prompt_id: str = Field(alias="promptId")
    prompt_version_id: str = Field(alias="promptVersionId")
    message_type: MessageType = Field(alias="schemaType")

    model_config = ConfigDict(
        populate_by_name=True,  # Allow both alias and Python names
        alias_generator=lambda s: "".join(
            word.capitalize() if i > 0 else word for i, word in enumerate(s.split("_"))
        ),
    )


class PromptSchemas(BaseModel):
    input: SchemaWithMetadata | None = None
    outputs: list[SchemaWithMetadata] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class MoxnMessageMetadata(BaseModel):
    message_id: str
    message_version_id: str
    prompt_id: str
    prompt_version_id: str


class MoxnBaseModel(BaseModel):
    """Base model that includes message metadata configuration"""

    model_version_config: dict[str, MoxnMessageMetadata | None] = {
        "metadata": None  # Initially None, must be set before model instantiation
    }

    @classmethod
    def set_metadata(cls, metadata: MoxnMessageMetadata) -> None:
        """Set the metadata for this model class"""
        cls.model_version_config["metadata"] = metadata


class CodegenResponse(BaseModel):
    """Response model for code generation prompts"""

    files: dict[str, str]


SchemaProperty.model_rebuild()
