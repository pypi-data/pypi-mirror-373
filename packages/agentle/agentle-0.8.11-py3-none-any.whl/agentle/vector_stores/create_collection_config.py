from typing import TypedDict

from agentle.vector_stores.distance import Distance


class CreateCollectionConfig(TypedDict):
    size: int
    distance: Distance
