from typing import TypedDict, NotRequired
from agentle.generations.providers.amazon.models.cache_point_block import (
    CachePointBlock,
)


class SystemMessage(TypedDict):
    text: str
    cachePoint: NotRequired[CachePointBlock]
