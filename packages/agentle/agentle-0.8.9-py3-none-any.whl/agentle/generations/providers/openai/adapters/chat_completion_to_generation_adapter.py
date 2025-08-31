from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from rsb.adapters.adapter import Adapter

from agentle.generations.models.generation.generation import Generation
from agentle.generations.models.generation.usage import Usage
from agentle.generations.providers.openai.adapters.openai_choice_to_choice_adapter import (
    OpenaiChoiceToChoiceAdapter,
)

if TYPE_CHECKING:
    from openai.types.chat.chat_completion import ChatCompletion
    from openai.types.chat.parsed_chat_completion import ParsedChatCompletion


class ChatCompletionToGenerationAdapter[T](
    Adapter["ChatCompletion | ParsedChatCompletion[T]", Generation[T]]
):
    def adapt(self, _f: ChatCompletion | ParsedChatCompletion[T]) -> Generation[T]:
        from openai.types.completion_usage import CompletionUsage

        completion = _f
        choice_adapter = OpenaiChoiceToChoiceAdapter[T]()

        usage = completion.usage or CompletionUsage(
            completion_tokens=0, prompt_tokens=0, total_tokens=0
        )

        return Generation(
            id=uuid.uuid4(),
            object="chat.generation",
            created=datetime.datetime.fromtimestamp(completion.created),
            model=completion.model,
            choices=[choice_adapter.adapt(choice) for choice in completion.choices],
            usage=Usage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            ),
        )
