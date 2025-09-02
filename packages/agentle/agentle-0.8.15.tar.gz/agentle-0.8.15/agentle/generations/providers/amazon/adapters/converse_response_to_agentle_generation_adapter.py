from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import datetime
from typing import TYPE_CHECKING, Any, cast, override
import uuid

from rsb.adapters.adapter import Adapter

from agentle.generations.models.generation.choice import Choice
from agentle.generations.models.generation.generation import Generation
from agentle.generations.models.generation.usage import Usage

from agentle.generations.providers.amazon.adapters.boto_message_to_agentle_message_adapter import (
    BotoMessageToAgentleMessageAdapter,
)

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime.type_defs import ConverseResponseTypeDef


@dataclass(frozen=True)
class ConverseResponseToAgentleGenerationAdapter[T](
    Adapter["ConverseResponseTypeDef", Generation[T]]
):
    model: str
    response_schema: type[T] | None = field(default=None)

    @override
    def adapt(self, _f: ConverseResponseTypeDef) -> Generation[T]:
        # Without Structured Outputs
        # b'{"metrics":{"latencyMs":1501},"output":{"message":{"content":[{"text":"Hello! It\'s nice to meet you. How are you doing today? Is there anything I can help you with?"}],"role":"assistant"}},"stopReason":"end_turn","usage":{"cacheReadInputTokenCount":0,"cacheReadInputTokens":0,"cacheWriteInputTokenCount":0,"cacheWriteInputTokens":0,"inputTokens":14,"outputTokens":27,"totalTokens":41}}'

        amazon_usage: Mapping[str, Any] = cast(Mapping[str, Any], _f["usage"])

        usage = Usage(
            prompt_tokens=amazon_usage["inputTokens"],
            completion_tokens=amazon_usage["outputTokens"],
        )

        _message_adater = BotoMessageToAgentleMessageAdapter(
            response_schema=self.response_schema
        )

        _bedrock_output = _f.get("output")
        _bedrock_message = _bedrock_output.get("message")

        if _bedrock_message is None:
            raise ValueError(
                "Could not get message from bedrock response."
                + f"Bedrock response: {_f}"
            )

        return Generation(
            id=uuid.uuid4(),
            model=self.model,
            object="chat.generation",
            choices=[Choice(index=0, message=_message_adater.adapt(_bedrock_message))],
            created=datetime.datetime.now(),
            usage=usage,
        )
