from typing import TypedDict
from agentle.generations.providers.amazon.models.response_message import (
    ResponseMessage,
)


class ConverseOutput(TypedDict):
    message: ResponseMessage
