from collections.abc import Mapping
from typing import TypedDict, Any


class ToolInputSchema(TypedDict):
    json: Mapping[str, Any]  # JSON Schema object
