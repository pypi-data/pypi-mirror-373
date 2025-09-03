from __future__ import annotations

from typing import TYPE_CHECKING

from rsb.adapters.adapter import Adapter

from agentle.generations.models.generation.choice import Choice
from agentle.generations.providers.openai.adapters.openai_message_to_generated_assistant_message import (
    OpenAIMessageToGeneratedAssistantMessageAdapter,
)

if TYPE_CHECKING:
    from openai.types.chat.chat_completion import Choice as OpenAIChoice
    from openai.types.chat.parsed_chat_completion import ParsedChoice


class OpenaiChoiceToChoiceAdapter[T](
    Adapter["OpenAIChoice | ParsedChoice[T]", Choice[T]]
):
    def adapt(self, _f: OpenAIChoice | ParsedChoice[T]) -> Choice[T]:
        openai_choice = _f
        return Choice(
            index=openai_choice.index,
            message=OpenAIMessageToGeneratedAssistantMessageAdapter[T]().adapt(
                openai_choice.message
            ),
        )
