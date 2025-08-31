from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast, override
from mypy_boto3_bedrock_runtime.type_defs import MessageOutputTypeDef
from rsb.adapters.adapter import Adapter

from agentle.generations.models.messages.generated_assistant_message import (
    GeneratedAssistantMessage,
)
from agentle.generations.providers.amazon.adapters.boto_content_to_agentle_part_adapter import (
    BotoContentToAgentlePartAdapter,
)

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime.type_defs import MessageOutputTypeDef


@dataclass(frozen=True)
class BotoMessageToAgentleMessageAdapter[T](
    Adapter[MessageOutputTypeDef, GeneratedAssistantMessage[T]]
):
    response_schema: type[T] | None = field(default=None)

    @override
    def adapt(self, _f: MessageOutputTypeDef) -> GeneratedAssistantMessage[T]:
        parsed = None
        if self.response_schema:
            from pydantic import BaseModel

            rs = cast(BaseModel, self.response_schema)
            bedrock_tool_use = _f.get("content")[0].get("toolUse")
            if bedrock_tool_use is None:
                raise ValueError(
                    f"Didn't receive structured output from Bedrock. output: {_f}"
                )

            structured_output = bedrock_tool_use.get("input")
            parsed = cast(T, rs.model_validate(structured_output))

        part_adapter = BotoContentToAgentlePartAdapter()

        content = _f.get("content")

        return GeneratedAssistantMessage[T](
            role="assistant",
            parts=[part_adapter.adapt(p) for p in content],
            parsed=cast(T, parsed),
        )
