from collections.abc import Sequence
from typing import TypedDict, NotRequired, Any
from agentle.generations.providers.amazon.models.message import Message
from agentle.generations.providers.amazon.models.system_message import SystemMessage
from agentle.generations.providers.amazon.models.inference_config import (
    InferenceConfig,
)
from agentle.generations.providers.amazon.models.tool_config import ToolConfig
from agentle.generations.providers.amazon.models.guardrail_config import (
    GuardrailConfig,
)


class ConverseRequest(TypedDict):
    modelId: str
    messages: Sequence[Message]
    system: NotRequired[Sequence[SystemMessage]]
    inferenceConfig: NotRequired[InferenceConfig]
    toolConfig: NotRequired[ToolConfig]
    guardrailConfig: NotRequired[GuardrailConfig]
    additionalModelRequestFields: NotRequired[dict[str, Any]]
    additionalModelResponseFieldPaths: NotRequired[Sequence[str]]
