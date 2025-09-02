from typing import TypedDict, Literal


class MessageStartEvent(TypedDict):
    role: Literal["assistant"]
