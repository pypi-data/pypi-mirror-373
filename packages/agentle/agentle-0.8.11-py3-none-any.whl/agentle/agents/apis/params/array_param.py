from collections.abc import Sequence
from typing import Any
from agentle.agents.apis.array_schema import ArraySchema
from agentle.agents.apis.endpoint_parameter import EndpointParameter
from agentle.agents.apis.object_schema import ObjectSchema
from agentle.agents.apis.parameter_location import ParameterLocation
from agentle.agents.apis.primitive_schema import PrimitiveSchema


def array_param(
    name: str,
    description: str,
    item_schema: ObjectSchema | ArraySchema | PrimitiveSchema,
    required: bool = False,
    min_items: int | None = None,
    max_items: int | None = None,
    location: ParameterLocation = ParameterLocation.QUERY,
    example: Sequence[Any] | None = None,
) -> EndpointParameter:
    """Create an array parameter."""
    return EndpointParameter(
        name=name,
        description=description,
        parameter_schema=ArraySchema(
            items=item_schema, min_items=min_items, max_items=max_items, example=example
        ),
        location=location,
        required=required,
    )
