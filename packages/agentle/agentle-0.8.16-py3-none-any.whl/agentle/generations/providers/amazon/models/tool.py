from typing import TypedDict
from agentle.generations.providers.amazon.models.tool_specification import (
    ToolSpecification,
)


class Tool(TypedDict):
    toolSpec: ToolSpecification
