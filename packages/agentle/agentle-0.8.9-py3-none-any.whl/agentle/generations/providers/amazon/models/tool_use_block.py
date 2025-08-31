from collections.abc import Mapping
from typing import TypedDict, Any


class ToolUseBlock(TypedDict):
    toolUseId: str
    name: str
    input: Mapping[str, Any]
