from rsb.models.base_model import BaseModel
from rsb.models.field import Field


class Collection(BaseModel):
    name: str
    indexed_vectors_count: int | None = Field(default=None)
