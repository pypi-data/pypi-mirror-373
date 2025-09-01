import base64
import imghdr
from typing import Literal, cast

# How many raw bytes of header we need to cover the longest magic prefix?
_HEADER_BYTES = 12

# Precompute how many base64 chars that is:
#   ceil(_HEADER_BYTES/3) * 4
_B64_CHARS = ((_HEADER_BYTES + 2) // 3) * 4


def infer_image_mime(
    b64: str,
) -> (
    Literal[
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/gif",
        "image/webp",
        "image/bmp",
        "image/tiff",
    ]
    | None
):
    """
    Infer an image MIME type from a (possibly Data-URI) Base64 string,
    without any third-party deps.
    Returns e.g. "image/png", "image/jpeg", "image/gif", or None.
    """
    # 1) strip data URI prefix if present
    if b64.startswith("data:"):
        try:
            header, b64 = b64.split(",", 1)
        except ValueError:
            return None

    # 2) decode only the header bytes
    try:
        blob = base64.b64decode(b64[:_B64_CHARS], validate=True)
    except ValueError:
        return None

    # 3) let imghdr do most of the work
    kind = imghdr.what(None, blob)
    if kind in ("jpeg", "png", "jpg", "gif", "webp"):
        # imghdr returns e.g. "jpeg" or "png" or "jpg" or "gif" or "webp"
        return cast(
            Literal["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"],
            f"image/{kind}",
        )

    # 4) manual magic-number fallbacks (if you need more formats)
    if blob.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if blob[:3] == b"GIF":
        return "image/gif"
    if blob[:2] == b"\xff\xd8":
        return "image/jpeg"
    # BMP
    if blob[:2] == b"BM":
        return "image/bmp"
    # TIFF (little or big endian)
    if blob[:4] in (b"II*\x00", b"MM\x00*"):
        return "image/tiff"
    # WebP (RIFF....WEBP)
    if blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "image/webp"

    return None
