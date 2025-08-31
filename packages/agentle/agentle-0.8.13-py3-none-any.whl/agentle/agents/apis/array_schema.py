from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal

from rsb.models.base_model import BaseModel
from rsb.models.field import Field

if TYPE_CHECKING:
    from agentle.agents.apis.object_schema import ObjectSchema
    from agentle.agents.apis.primitive_schema import PrimitiveSchema


class ArraySchema(BaseModel):
    """Schema definition for array parameters."""

    type: Literal["array"] = Field(default="array")

    items: ObjectSchema | ArraySchema | PrimitiveSchema = Field(
        description="Schema for array items"
    )

    min_items: int | None = Field(default=None)
    max_items: int | None = Field(default=None)

    example: Sequence[Any] | None = Field(default=None)
