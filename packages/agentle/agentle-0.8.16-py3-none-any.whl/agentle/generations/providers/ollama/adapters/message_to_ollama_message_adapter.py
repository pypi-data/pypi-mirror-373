from __future__ import annotations

from collections.abc import MutableSequence
from typing import TYPE_CHECKING, override

from rsb.adapters.adapter import Adapter

from agentle.generations.models.message_parts.file import FilePart
from agentle.generations.models.message_parts.text import TextPart
from agentle.generations.models.message_parts.tool_execution_suggestion import (
    ToolExecutionSuggestion,
)
from agentle.generations.models.messages.assistant_message import AssistantMessage
from agentle.generations.models.messages.developer_message import DeveloperMessage
from agentle.generations.models.messages.user_message import UserMessage
from agentle.generations.tools.tool import Tool
from agentle.generations.tools.tool_execution_result import ToolExecutionResult

if TYPE_CHECKING:
    from ollama._types import Message


class MessageToOllamaMessageAdapter(
    Adapter[DeveloperMessage | UserMessage | AssistantMessage, "Message"]
):
    @override
    def adapt(self, _f: DeveloperMessage | UserMessage | AssistantMessage) -> Message:
        from ollama._types import Image, Message

        image_parts: MutableSequence[Image] = []
        text_parts: MutableSequence[
            TextPart | Tool | ToolExecutionSuggestion | ToolExecutionResult
        ] = []
        tool_parts: MutableSequence[Message.ToolCall] = []
        for part in _f.parts:
            if isinstance(part, FilePart):
                if part.mime_type.startswith("image/"):
                    image_parts.append(Image(value=part.data))
            else:
                if isinstance(part, ToolExecutionSuggestion):
                    tool_parts.append(
                        Message.ToolCall(
                            function=Message.ToolCall.Function(
                                name=part.tool_name, arguments=part.args
                            )
                        )
                    )

                text_parts.append(part)

        if isinstance(_f, DeveloperMessage):
            role = "system"
        elif isinstance(_f, AssistantMessage):
            role = "assistant"
        else:
            role = "user"

        message = Message(
            role=role,
            content="".join([str(p.text) for p in text_parts]) if text_parts else None,
            images=image_parts,
            tool_calls=[],
        )

        return message
