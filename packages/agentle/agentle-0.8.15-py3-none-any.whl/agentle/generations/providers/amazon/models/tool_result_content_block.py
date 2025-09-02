from collections.abc import Mapping
from typing import TypedDict, NotRequired, Any
from agentle.generations.providers.amazon.models.image_block import ImageBlock
from agentle.generations.providers.amazon.models.document_block import DocumentBlock


class ToolResultContentBlock(TypedDict):
    text: NotRequired[str]
    json: NotRequired[Mapping[str, Any]]
    image: NotRequired[ImageBlock]
    document: NotRequired[DocumentBlock]
