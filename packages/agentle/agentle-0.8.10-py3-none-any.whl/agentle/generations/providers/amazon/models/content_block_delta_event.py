from typing import TypedDict
from agentle.generations.providers.amazon.models.text_delta import TextDelta
from agentle.generations.providers.amazon.models.tool_use_delta import ToolUseDelta


class ContentBlockDeltaEvent(TypedDict):
    contentBlockIndex: int
    delta: TextDelta | ToolUseDelta
