from collections.abc import Sequence
from typing import TypedDict, NotRequired


class GuardrailContentBlock(TypedDict):
    text: NotRequired[str]
    qualifiers: NotRequired[Sequence[str]]
