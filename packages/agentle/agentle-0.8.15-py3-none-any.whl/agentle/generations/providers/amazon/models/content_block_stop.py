from typing import TypedDict
from agentle.generations.providers.amazon.models.content_block_stop_event import (
    ContentBlockStopEvent,
)


class ContentBlockStop(TypedDict):
    stop: ContentBlockStopEvent
