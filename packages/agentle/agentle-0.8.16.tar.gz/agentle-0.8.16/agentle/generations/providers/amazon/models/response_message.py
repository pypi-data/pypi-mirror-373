from collections.abc import Sequence
from typing import TypedDict, Literal
from agentle.generations.providers.amazon.models.content_block import ContentBlock


class ResponseMessage(TypedDict):
    role: Literal["assistant"]
    content: Sequence[ContentBlock]
