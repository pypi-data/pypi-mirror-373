from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Literal
from uuid import uuid4

from pydantic import Field

from moxn_types.blocks.base import BaseContent, BlockType

if TYPE_CHECKING:
    from google.genai.types import File as GoogleFile
else:
    GoogleFile = Any


class MediaDataPDFFormat(str, Enum):
    BASE64 = "base64"
    BYTES = "bytes"
    GOOGLE_FILE = "google_file"
    GOOGLE_FILE_REFERENCE = "google_file_reference"
    LOCAL_FILE = "local_file"
    OPENAI_FILE_REFERENCE = "openai_file_reference"
    URL = "url"


class _PDFBase(BaseContent):
    """Base class for PDF content with common properties."""

    block_type: ClassVar[Literal[BlockType.FILE]] = BlockType.FILE
    media_type: Literal["application/pdf"] = "application/pdf"


class MediaDataPDFFromBase64Model(_PDFBase):
    """
    PDF of mime type pdf encoded in base64.
    """

    type: Literal[MediaDataPDFFormat.BASE64] = MediaDataPDFFormat.BASE64
    base64: str
    filename: str = Field(default_factory=lambda: f"file-{uuid4()}.pdf")


class MediaDataPDFFromBytesModel(_PDFBase):
    """
    PDF of mime type pdf encoded in bytes.
    """

    type: Literal[MediaDataPDFFormat.BYTES] = MediaDataPDFFormat.BYTES
    bytes: bytes
    filename: str = Field(default_factory=lambda: f"file-{uuid4()}.pdf")


class MediaDataPDFFromURLModel(_PDFBase):
    """
    PDF of mime type pdf encoded in url. URL must be a valid pdf url accessible via http/https.
    Note: For Google Vertex AI, public HTTP URLs are not supported - use GCS URIs instead.
    """

    type: Literal[MediaDataPDFFormat.URL] = MediaDataPDFFormat.URL
    url: str
    filename: str = Field(default_factory=lambda: f"file-{uuid4()}.pdf")


class MediaDataPDFFromOpenAIChatFileReferenceModel(_PDFBase):
    """
    PDF of mime type pdf encoded in OpenAI File ID Reference.
    """

    type: Literal[MediaDataPDFFormat.OPENAI_FILE_REFERENCE] = (
        MediaDataPDFFormat.OPENAI_FILE_REFERENCE
    )
    file_id: str


class MediaDataPDFFromGoogleFileModel(_PDFBase):
    """
    PDF of mime type pdf encoded in Google File.
    """

    type: Literal[MediaDataPDFFormat.GOOGLE_FILE] = MediaDataPDFFormat.GOOGLE_FILE
    file: GoogleFile


class MediaDataPDFFromGoogleFileReferenceModel(_PDFBase):
    """
    PDF of mime type pdf encoded in Google File ID Reference.
    For Gemini Developer API: can be a types.File ID from client.files.upload()
    For Vertex AI: must be a GCS URI (gs://) with specified MIME type
    """

    type: Literal[MediaDataPDFFormat.GOOGLE_FILE_REFERENCE] = (
        MediaDataPDFFormat.GOOGLE_FILE_REFERENCE
    )
    uri: str


class MediaDataPDFFromLocalFileModel(_PDFBase):
    """
    PDF of mime type pdf encoded in local file.
    """

    type: Literal[MediaDataPDFFormat.LOCAL_FILE] = MediaDataPDFFormat.LOCAL_FILE
    filepath: Path
    filename: str = Field(default_factory=lambda: f"file-{uuid4()}.pdf")


_PDFContentFromSourceTypes = (
    MediaDataPDFFromBase64Model
    | MediaDataPDFFromBytesModel
    | MediaDataPDFFromURLModel
    | MediaDataPDFFromOpenAIChatFileReferenceModel
    | MediaDataPDFFromGoogleFileModel
    | MediaDataPDFFromGoogleFileReferenceModel
)
PDFContentFromSourceModel = Annotated[
    _PDFContentFromSourceTypes,
    Field(discriminator="type"),
]
