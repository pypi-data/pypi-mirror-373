from typing import TypedDict
from agentle.generations.providers.amazon.models.tool_input_schema import (
    ToolInputSchema,
)


class ToolSpecification(TypedDict):
    name: str
    description: str
    inputSchema: ToolInputSchema
