from typing import TypedDict
from agentle.generations.providers.amazon.models.tool_use_block import ToolUseBlock


class ToolUseContent(TypedDict):
    toolUse: ToolUseBlock
