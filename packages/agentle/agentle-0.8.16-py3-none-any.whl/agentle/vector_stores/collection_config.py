from rsb.models.base_model import BaseModel
from rsb.models.field import Field

from agentle.vector_stores.distance import Distance


class CollectionConfig(BaseModel):
    vectors_size: int = Field(description="The size of the collection vectors")
    distance: Distance = Field(description="Distance calculation method.")
