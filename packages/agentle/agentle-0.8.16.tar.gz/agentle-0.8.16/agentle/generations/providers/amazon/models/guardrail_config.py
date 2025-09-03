from typing import TypedDict, Literal, NotRequired


class GuardrailConfig(TypedDict):
    guardrailIdentifier: str
    guardrailVersion: str
    trace: NotRequired[Literal["enabled", "disabled"]]
