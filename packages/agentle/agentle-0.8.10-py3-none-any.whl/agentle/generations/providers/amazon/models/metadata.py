from typing import TypedDict
from agentle.generations.providers.amazon.models.usage import Usage
from agentle.generations.providers.amazon.models.converse_metrics import (
    ConverseMetrics,
)


class Metadata(TypedDict):
    usage: Usage
    metrics: ConverseMetrics
