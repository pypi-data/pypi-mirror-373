from typing import TypedDict
from agentle.generations.providers.amazon.models.cache_point_block import (
    CachePointBlock,
)


class CachePointContent(TypedDict):
    cachePoint: CachePointBlock
