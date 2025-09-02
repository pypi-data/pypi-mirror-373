from collections.abc import Sequence
from typing import Literal, NotRequired, TypedDict

from agentle.generations.providers.amazon.models.tool_result_content_block import (
    ToolResultContentBlock,
)


class ToolResultBlock(TypedDict):
    toolUseId: str
    content: Sequence[ToolResultContentBlock]
    status: NotRequired[Literal["success", "error"]]
