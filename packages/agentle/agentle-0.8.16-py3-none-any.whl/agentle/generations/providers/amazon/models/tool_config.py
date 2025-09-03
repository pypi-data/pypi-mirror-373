from collections.abc import Sequence
from typing import TypedDict, NotRequired
from agentle.generations.providers.amazon.models.tool import Tool
from agentle.generations.providers.amazon.models.tool_choice import ToolChoice


class ToolConfig(TypedDict):
    tools: Sequence[Tool]
    toolChoice: NotRequired[ToolChoice]
