from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Literal

from pydantic import Field

from moxn_types.blocks.base import BaseContent, BlockType

if TYPE_CHECKING:
    from google.genai.types import File as GoogleFile
else:
    GoogleFile = Any


class MediaDataImageFormat(str, Enum):
    BASE64 = "base64"
    BYTES = "bytes"
    GOOGLE_FILE = "google_file"
    GOOGLE_FILE_REFERENCE = "google_file_reference"
    LOCAL_FILE = "local_file"
    URL = "url"


class _ImageBase(BaseContent):
    """Base class for image content with common properties."""

    block_type: ClassVar[Literal[BlockType.IMAGE]] = BlockType.IMAGE

    media_type: Literal["image/jpeg", "image/png", "image/gif", "image/webp"]


class MediaImageFromBase64Model(_ImageBase):
    """
    Image encoded in base64 format.
    """

    type: Literal[MediaDataImageFormat.BASE64] = MediaDataImageFormat.BASE64
    base64: str


class MediaImageFromBytesModel(_ImageBase):
    """
    Image provided as raw bytes.
    """

    type: Literal[MediaDataImageFormat.BYTES] = MediaDataImageFormat.BYTES
    bytes: bytes


class MediaImageFromURLModel(_ImageBase):
    """
    Image referenced by a URL.
    Note: For Google Vertex AI, public HTTP URLs are NOT supported for images.
    """

    type: Literal[MediaDataImageFormat.URL] = MediaDataImageFormat.URL
    url: str


class MediaImageFromLocalFileModel(_ImageBase):
    """
    Image loaded from a local file path.
    """

    type: Literal[MediaDataImageFormat.LOCAL_FILE] = MediaDataImageFormat.LOCAL_FILE
    filepath: Path


class MediaImageFromGoogleFileModel(_ImageBase):
    """
    Image provided as a Google File object.
    Only supported by Google Gemini.
    """

    type: Literal[MediaDataImageFormat.GOOGLE_FILE] = MediaDataImageFormat.GOOGLE_FILE
    file: GoogleFile


class MediaImageFromGoogleFileReferenceModel(_ImageBase):
    """
    Image referenced by a Google File URI.
    For Gemini Developer API: can be any URI
    For Vertex AI: must be a GCS URI (gs://)
    """

    type: Literal[MediaDataImageFormat.GOOGLE_FILE_REFERENCE] = (
        MediaDataImageFormat.GOOGLE_FILE_REFERENCE
    )
    uri: str  # gs://


_ImageContentFromSourceTypes = (
    MediaImageFromBase64Model
    | MediaImageFromBytesModel
    | MediaImageFromURLModel
    | MediaImageFromLocalFileModel
    | MediaImageFromGoogleFileModel
    | MediaImageFromGoogleFileReferenceModel
)
ImageContentFromSourceModel = Annotated[
    _ImageContentFromSourceTypes,
    Field(discriminator="type"),
]
