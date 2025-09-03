from typing import TypedDict
from agentle.generations.providers.amazon.models.guardrail_content_block import (
    GuardrailContentBlock,
)


class GuardrailContent(TypedDict):
    guardContent: GuardrailContentBlock
