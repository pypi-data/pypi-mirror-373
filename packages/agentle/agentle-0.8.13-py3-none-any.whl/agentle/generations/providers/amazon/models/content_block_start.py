from typing import TypedDict

from agentle.generations.providers.amazon.models.content_block_start_event import (
    ContentBlockStartEvent,
)


class ContentBlockStart(TypedDict):
    start: ContentBlockStartEvent
