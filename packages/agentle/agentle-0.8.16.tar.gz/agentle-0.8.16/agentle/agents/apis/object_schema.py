"""
Clean replacement for the existing endpoint parameter implementation.
This replaces the original classes with proper object parameter support.

Simply replace the existing EndpointParameter and related classes with these improved versions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Literal

from rsb.models.base_model import BaseModel
from rsb.models.field import Field

if TYPE_CHECKING:
    from agentle.agents.apis.array_schema import ArraySchema
    from agentle.agents.apis.primitive_schema import PrimitiveSchema


class ObjectSchema(BaseModel):
    """Schema definition for object parameters."""

    type: Literal["object"] = Field(default="object")

    properties: Mapping[str, ObjectSchema | ArraySchema | PrimitiveSchema] = Field(
        default_factory=dict, description="Properties of the object with their schemas"
    )

    required: Sequence[str] = Field(
        default_factory=list, description="List of required property names"
    )

    additional_properties: bool = Field(
        default=True,
        description="Whether additional properties beyond those defined are allowed",
    )

    example: Mapping[str, Any] | None = Field(
        default=None, description="Example value for the object"
    )
