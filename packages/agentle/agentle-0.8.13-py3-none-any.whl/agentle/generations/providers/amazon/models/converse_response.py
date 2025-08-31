from collections.abc import Mapping
from typing import TypedDict, Literal, NotRequired, Any
from agentle.generations.providers.amazon.models.converse_output import ConverseOutput
from agentle.generations.providers.amazon.models.usage import Usage
from agentle.generations.providers.amazon.models.converse_metrics import (
    ConverseMetrics,
)


class ConverseResponse(TypedDict):
    output: ConverseOutput
    stopReason: Literal[
        "end_turn",
        "tool_use",
        "max_tokens",
        "stop_sequence",
        "guardrail_intervened",
        "content_filtered",
    ]
    usage: Usage
    metrics: ConverseMetrics
    additionalModelResponseFields: NotRequired[Mapping[str, Any]]
