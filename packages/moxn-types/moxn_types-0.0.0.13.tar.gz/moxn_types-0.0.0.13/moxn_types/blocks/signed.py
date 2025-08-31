from datetime import datetime
from typing import ClassVar, Literal
from uuid import uuid4

from pydantic import Field

from moxn_types.blocks.base import BaseContent, BlockType


class SignedURLContentModel(BaseContent):
    block_type: ClassVar[Literal[BlockType.SIGNED]] = BlockType.SIGNED
    file_path: str
    expiration: datetime | None = None
    ttl_seconds: int = 3600
    buffer_seconds: int = 300
    signed_url: str | None = None


class SignedURLImageContentModel(SignedURLContentModel):
    type: Literal["url"] = "url"  # Assuming MediaDataImageFormat.URL is "url"
    media_type: Literal["image/jpeg", "image/png", "image/gif", "image/webp"]


class SignedURLPDFContentModel(SignedURLContentModel):
    type: Literal["url"] = "url"  # Assuming MediaDataPDFFormat.URL is "url"
    media_type: Literal["application/pdf"] = "application/pdf"
    filename: str = Field(default_factory=lambda: f"file-{uuid4()}.pdf")
