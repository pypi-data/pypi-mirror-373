from collections.abc import Sequence
from typing import Literal, TypedDict

from agentle.generations.providers.amazon.models.content_block import ContentBlock


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: Sequence[ContentBlock]
