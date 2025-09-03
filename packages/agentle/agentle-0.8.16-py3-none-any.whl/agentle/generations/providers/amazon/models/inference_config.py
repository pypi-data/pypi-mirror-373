from collections.abc import Sequence
from typing import NotRequired, TypedDict


class InferenceConfig(TypedDict):
    maxTokens: NotRequired[int]
    temperature: NotRequired[float]
    topP: NotRequired[float]
    stopSequences: NotRequired[Sequence[str]]
