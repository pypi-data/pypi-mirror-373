from typing import TypedDict
from agentle.generations.providers.amazon.models.content_block_delta_event import (
    ContentBlockDeltaEvent,
)


class ContentBlockDelta(TypedDict):
    delta: ContentBlockDeltaEvent
