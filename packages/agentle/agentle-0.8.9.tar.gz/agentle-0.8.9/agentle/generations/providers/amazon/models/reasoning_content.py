from typing import TypedDict
from agentle.generations.providers.amazon.models.reasoning_content_block import (
    ReasoningContentBlock,
)


class ReasoningContent(TypedDict):
    reasoningContent: ReasoningContentBlock
