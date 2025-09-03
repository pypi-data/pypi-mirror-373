from typing import TypedDict
from agentle.generations.providers.amazon.models.tool_use_delta_block import (
    ToolUseDeltaBlock,
)


class ToolUseDelta(TypedDict):
    toolUse: ToolUseDeltaBlock
