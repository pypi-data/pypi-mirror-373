"""Content block model for DTOs - uses flexible RawContentBlock for API parsing."""

from pydantic import TypeAdapter
from moxn_types.blocks.raw_block import RawContentBlock

# For DTOs, we use RawContentBlock to ensure flexible API parsing
ContentBlockModel = RawContentBlock

ContentBlockAdapter: TypeAdapter[ContentBlockModel] = TypeAdapter(ContentBlockModel)
