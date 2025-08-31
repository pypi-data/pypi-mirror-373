from __future__ import annotations

from typing import TYPE_CHECKING, override

from rsb.adapters.adapter import Adapter

from agentle.generations.models.message_parts.text import TextPart
from agentle.generations.models.message_parts.tool_execution_suggestion import (
    ToolExecutionSuggestion,
)

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime.type_defs import ContentBlockOutputTypeDef


class BotoContentToAgentlePartAdapter(
    Adapter[
        "ContentBlockOutputTypeDef",
        TextPart | ToolExecutionSuggestion,
    ]
):
    @override
    def adapt(
        self,
        _f: ContentBlockOutputTypeDef,
    ) -> TextPart | ToolExecutionSuggestion:
        text = _f.get("text")
        if text:
            return TextPart(text=text)

        tool_use = _f.get("toolUse")
        if tool_use:
            return ToolExecutionSuggestion(
                id=tool_use["toolUseId"],
                tool_name=tool_use["name"],
                args=tool_use["input"],
            )

        raise ValueError(
            "Could not adapt the Bedrock contents to Agentle Contents"
            + f"Invalid part: {_f}"
        )
