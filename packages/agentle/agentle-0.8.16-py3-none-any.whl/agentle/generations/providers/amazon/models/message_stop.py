from typing import TypedDict
from agentle.generations.providers.amazon.models.message_stop_event import (
    MessageStopEvent,
)


class MessageStop(TypedDict):
    stop: MessageStopEvent
