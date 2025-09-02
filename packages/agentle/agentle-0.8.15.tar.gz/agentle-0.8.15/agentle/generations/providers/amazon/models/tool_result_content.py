from typing import TypedDict
from agentle.generations.providers.amazon.models.tool_result_block import (
    ToolResultBlock,
)


class ToolResultContent(TypedDict):
    toolResult: ToolResultBlock
